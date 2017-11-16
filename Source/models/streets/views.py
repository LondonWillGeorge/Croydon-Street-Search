# In this model, views.py files are the Flask Blueprint for this object.
# ie they describe what HTTP API endpoints are associated to objects of this class.
from flask import Blueprint, render_template, request, redirect
import Source.models.streets.street as Streets
from Source.common.utils import Utils

__author__ = 'Will Croxford'


streets_blueprint = Blueprint('streets', __name__)


@streets_blueprint.route('/new_street.jinja2', methods=['POST', 'GET'])
def newstreet():
    return render_template('streets/new_street.jinja2')


# used for converting form index value of road class to road type.
def road(index):
    roadtypes = {1: 'Class A', 2: 'Class B', 3: 'Class C'}
    return roadtypes.get(index, "Unclassified")


# used to concatenate with road number for saving to Mongo, eg B + 241 = 'B241'
def letter(index):
    letters = {1: 'A', 2: 'B', 3: 'C'}
    return letters.get(index, "A")


# used to convert index number returned by form to borough name to be saved in database.
def borough(index):
    boro_names = {1: "London Borough of Lambeth", 2: "London Borough of Sutton",
                  3: "Reigate and Banstead District Council", 4: "London Borough of Bromley",
                  5: "London Borough of Merton", 6: "Tandridge District Council"}
    return boro_names.get(index, "None")


# Split off from create_street method, checks for number range, road type street characteristics,
# because McCabe complexity was > 10 before, violating PEP8 (too many conditions in one method basically)
def numrange_roadtype(req):
    maintained = int(req.form['maint'])  # 0 to 2, for Croydon, TfL, private
    # adoption field - Adopted, Unadopted, don't want any nulls!
    if maintained == 2:
        adoption = 'Unadopted'
    else:
        adoption = 'Adopted'

    onb = req.form['onb']  # integer non-zero or 'None'
    try:
        onb = int(onb)
    except (TypeError, ValueError, KeyError):
        onb = 'None'
    # leave as 'None' instead of None, best to avoid null value?
    # if any field(s) disabled, form will be unable to request name, so will throw an exception.
    try:
        one = int(req.form['one'])  # integer non-zero or 'None'
        enb = int(req.form['enb'])  # integer non-zero or 'None'
        ene = int(req.form['ene'])  # integer non-zero or 'None'
        # for any of these which are still 'None' on form, sets it to None (null) value ready for database.
        # leave as 'None' as street list deals with this, and better NOT to have null values surely?
        # one, enb, ene = [(None if x is 'None' else x) for x in [one, enb, ene]]
        # trying to catch all likely errors anyway, bad practice to catch with blanket except
    except (TypeError, ValueError, KeyError):
        one, enb, ene = ['None' for _ in range(3)]

    rdclass = int(req.form['rdclass'])  # 0 to 3, corresponding 0 'Unclassified' 'TFL' or 1 'Class A' 2 B 3 C
    # NB keeping the original database values consistent, even though ends up convoluting the process here,
    # so the Road Class field in db will be TFL if maintained by TFL,
    # but can still be saved as A, B or C road in this app.
    if maintained == 1:
        roadcls = 'TFL'
    else:
        roadcls = road(rdclass)

    try:
        rdnum = req.form['rdnum']  # should be number only from client regex
    except (KeyError, ValueError, TypeError, NameError):
        rdnum = 'None'
    if rdclass != 0 and rdnum != 'None':
        roadnum = letter(rdclass) + rdnum
    else:
        roadnum = 'None'

    length = int(req.form['length'])  # integer non-zero, convert integer to save
    return onb, one, enb, ene, adoption, roadcls, length, roadnum


# 3 Questions collection of street characteristics also moved into separate method here to decrease complexity.
# At 6/11/17, these are the last 3 yes/no questions (and related details if yes) from the Add Dummy Street form.
def tflside_boro_split(req):
    tfl = int(req.form['TfL'])  # will be 0 or 1 (for No or Yes), convert integer to save
    try:
        # string for road name client regex should ensure it is letter and number only.
        tflroad = req.form['TfLroad']
    except (KeyError, ValueError, TypeError, NameError):
        tflroad = 'None'  # OK save as is
    # cross1 from 0 to 6, if cross1 == 0, then ignore cross2, and set cross_boro to 0 (No)
    cross1 = int(req.form['cross1'])
    try:
        cross2 = int(req.form['cross2'])  # from 0 to 6
    except (KeyError, ValueError, TypeError, NameError):
        cross2 = 0
    if cross1 == 0:
        cross_boro = 0
        boro1 = 'None'
        boro2 = 'None'
    else:
        cross_boro = 1
        boro1 = borough(cross1)
        boro2 = borough(cross2)

    split = int(req.form['Split'])  # will be 0 or 1 (for No or Yes)
    # assemble split road status from checkboxes ticked on form. If they're disabled (no split road) status 'None'.
    # values on form are same as actual values to save in statuslist in database: Nil Local London Strategic or TfL
    # statuslist concatenates them eg 'Local/London' etc.
    if split == 0:
        status = 'None'
    else:
        try:
            statuslist = req.form.getlist('status')  # list with poss values 1 to 5 from checkboxes
            status = statuslist[0]
            for x in range(1, len(statuslist)):
                status += ("/" + statuslist[x])
        except (KeyError, ValueError, TypeError, NameError):
            status = 'None'
    return tfl, tflroad, cross_boro, boro1, boro2, split, status


# Processes all the street fields from create dummy street form.
# Remember browser sends 'name' and 'value' attributes from form, not the id attr.
@streets_blueprint.route('/new_street/created', methods=['POST', 'GET'])
def create_street():
    if request.method == 'POST':
        # try except loop here, and condition for GET/POST..
        street = request.form['stname'].strip()
        district = request.form['distr']  # 0 to 11 corresp. to districts

        # method split off here to reduce complexity of this function (McCabe complexity to be pedantic)
        onb, one, enb, ene, adoption, roadcls, length, roadnum = numrange_roadtype(request)

        # method split here for 3 questions data..
        tfl, tflroad, cross_boro, boro1, boro2, split, status = tflside_boro_split(request)

        dummy = True
        visible = True
        # result_message shows info on street which has been created, to show user the street has been
        # created successfully. Or if exception and it fails, shows the user an error message.
        try:
            created = Streets.Street(street, district, dummy, visible, onb, one, enb, ene, adoption, roadcls, length,
                                     roadnum, tfl, tflroad, cross_boro, boro1, boro2, split, status)
            created.save_to_mongo()

            result_message = """Congratulations! You just created a new street section \"{0}\", in the District:
                             {1}, with a unique ID number in this database of <span class=\"brgreen\">{2}
                      </span>. You can now test by searching for this street name, or even using this ID number in
                      the street list/report results URL.""" .format(street, created.long_dist, created.id)
        # in a final production, would want to log all the error details perhaps, assuming this error will be rare!
        except (TypeError, ValueError, KeyError):
            result_message = """Sorry, but a key, value or type error has occurred. Please try again, or you can email
                             the webmaster with any details of when your error occurred."""
        except (ImportError, ModuleNotFoundError):
            result_message = """Sorry, but a 'module not found' or 'import' error has occurred. Please try again, or you
                            can email the webmaster with any details of when your error occurred."""

    # Below for HTTP GET request, eg user hits F5 refresh button, redirect to blank new dummy street page.
    # NB PyCharm shows type error warning message on argument for redirect_url here, this warning not relevant I think:
    # expected type 'Utils' got 'str' instead.
    else:
        return redirect(Utils.redirect_url('streets.newstreet'))

    return render_template('streets/new_street.jinja2', result=result_message)
