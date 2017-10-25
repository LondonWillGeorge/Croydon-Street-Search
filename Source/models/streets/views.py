# In this model, views.py files are the Flask Blueprint for this object.
# ie they describe what HTTP API endpoints are associated to objects of this class.
import flask
from flask import Blueprint, render_template, request, redirect, url_for
import Source.models.streets.street as Streets
from Source.common.utils import Utils

__author__ = 'Will Croxford'


streets_blueprint = Blueprint('streets', __name__)

@streets_blueprint.route('/new_street.jinja2', methods=['POST', 'GET'])
def newstreet():
    return render_template('streets/new_street.jinja2')

# used for converting form index value of road class to road type.
def road(index):
    Roadtypes = {1: 'Class A', 2: 'Class B', 3: 'Class C'}
    return Roadtypes.get(index, "Unclassified")

# used to concatenate with road number for saving to Mongo, eg B + 241 = 'B241'
def letter(index):
    Letters = {1: 'A', 2: 'B', 3: 'C'}
    return Letters.get(index, "A")

def borough(index):
    boro_names = {1: "London Borough of Lambeth", 2: "London Borough of Sutton",
                  3: "Reigate and Banstead District Council", 4: "London Borough of Bromley",
                  5: "London Borough of Merton", 6: "Tandridge District Council"}
    return boro_names.get(index, "None")

# Remember browser sends name or value attributes from form, not id attr.
@streets_blueprint.route('/new_street/created', methods= ['POST', 'GET'])
def create_street():
    if request.method == 'POST':
        # try except loop here, and condition for GET/POST..
        street = request.form['stname'].strip()
        district = request.form['distr'] # 0 to 11 corresp. to districts
        maintained = int(request.form['maint']) # 0 to 2, for Croydon, TfL, private
        # adoption field - Adopted, Unadopted, don't want any nulls!
        if maintained == 2:
            adoption = 'Unadopted'
        else:
            adoption = 'Adopted'
        onb = request.form['onb'] # integer non-zero or 'None'
        try:
            onb = int(onb)
        except:
            onb = 'None'
        # leave as 'None' instead of None, best to avoid null value?
        # if any field(s) disabled, form will be unable to request name, so will throw an exception.
        try:
            one = int(request.form['one']) # integer non-zero or 'None'
            enb = int(request.form['enb']) # integer non-zero or 'None'
            ene = int(request.form['ene']) # integer non-zero or 'None'
            # for any of these which are still 'None' on form, sets it to None (null) value ready for database.
            # leave as 'None' as street list deals with this, and better NOT to have null values surely?
            # one, enb, ene = [(None if x is 'None' else x) for x in [one, enb, ene]]
        except:
            one, enb, ene = ['None' for _ in range(3)]

        rdclass = int(request.form['rdclass']) # 0 to 3, corresponding 0 'Unclassified' 'TFL' or 1 'Class A' 2 B 3 C
        # NB keeping the original data values consistent, even though ends up convoluted to process here,
        # so the Road Class field in db will be TFL if maintained by TFL, but can still be saved A, B or C road in this app.
        if maintained == 1:
            roadcls = 'TFL'
        else:
            roadcls = road(rdclass)

        try:
            rdnum = request.form['rdnum'] # should be number only from client regex
        except:
            rdnum = 'None'
        if rdclass != 0 and rdnum != 'None':
            roadnum = letter(rdclass) + rdnum
        else:
            roadnum = 'None'

        length = int(request.form['length']) # integer non-zero, convert integer to save
        TfL = int(request.form['TfL']) # will be 0 or 1 (for No or Yes), convert integer to save
        try:
            TfLroad = request.form['TfLroad'] #string for road name client regex should ensure it is letter and number only.
        except:
            TfLroad = 'None' # OK save as is
        cross1 = int(request.form['cross1']) # from 0 to 6, if cross1 == 0, then ignore cross2, and set cross_boro to 0 (No)
        try:
            cross2 = int(request.form['cross2']) # from 0 to 6
        except:
            cross2 = 0
        if cross1 == 0:
            cross_boro = 0; boro1 = 'None'; boro2 = 'None'
        else:
            cross_boro = 1; boro1 = borough(cross1); boro2 = borough(cross2)

        Split = int(request.form['Split']) # will be 0 or 1 (for No or Yes)
        # assemble split road status from checkboxes ticked on form. If they're disabled (no split road) status 'None'.
        # values on form are same as actual values to save in statuslist in database: Nil Local London Strategic or TfL
        # statuslist concatenates eg 'Local/London' etc.
        if Split == 0:
            status = 'None'
        else:
            try:
                statuslist = request.form.getlist('status') # list with poss values 1 to 5 from checkboxes
                status = statuslist[0]
                for x in range(1, len(statuslist)):
                    status += ("/" + statuslist[x])
            except:
                status = 'None'
        dummy = True
        visible = True
        # changed long_dist key now... distr should produce right number directly
        # string with success message and info on street which has been created, to show user the street has been
        # created successfully. Or if exception and it fails, shows the user an error message.
        try:
            created = Streets.Street(street, district, dummy, visible, onb, one, enb, ene, adoption, roadcls, length,
                                     roadnum, TfL, TfLroad, cross_boro, boro1, boro2, Split, status)
            # error it is creating 3 new streets with same details, consecutive IDs...
            created.save_to_mongo()

            result_message = "Congratulations! You just created a new street section \"{0}\", in the District: \
                             {1}, with a unique ID number in this database of <span class=\"brgreen\">{2} \
                      </span>. You can now test by searching for this street name, or even using this ID number in \
                      the street list/report results URL." .format(street, created.long_dist, created.id)
        except:
            result_message = "Sorry, but an error has occurred. Please try again, or you can email the webmaster with any details" \
                      " of when your error occurred."
    # if this is HTTP GET request, eg user hits F5 refresh button, redirect to blank new dummy street page.
    # NB PyCharm shows warning message on argument for redirect_url here, this warning not valid, I think
    # something to do with function being method from imported class in other module.
    else:
        return redirect(Utils.redirect_url('streets.newstreet'))

    return render_template('streets/new_street.jinja2', result=result_message)
