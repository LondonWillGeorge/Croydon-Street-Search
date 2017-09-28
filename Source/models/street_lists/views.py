# In this model, views.py files are the Flask Blueprint for this object.
# ie they describe what HTTP API endpoints are associated to objects of this class.
import flask
from flask import Blueprint, render_template, request, redirect, url_for

import Source.models.street_lists.street_list as Lists

__author__ = 'jslvtr'


street_list_blueprint = Blueprint('street_lists', __name__)

# or is it request.form['list_id'] or something like this? or just <list_id>?

# </list_id> where's token error coming from?
# , methods = ['GET', 'POST'] method not allowed error solved by POST method in route, but still Bad Request.

@street_list_blueprint.route('/', methods=['POST', 'GET'])
def get_streetlist():
    street = request.form['street'].strip() # strip trailing spaces form inputs, so blanks end up as -- in URL route.
    # 20-9-17 however, regex validation on client side has already ensured no trailing spaces anyway.
    number = request.form['number'].strip()
    c1 = request.form['c1'].strip()
    c2 = request.form['c2'].strip()
    c3 = request.form['c3'].strip()
    # if any variables are "" or None, below list comprehension sets to '--' to attempt a RESTful URL string.
    number, c1, c2, c3 = ['--' if (x == "" or x is None) else x for x in [number, c1, c2, c3]]

    # below tried to serialize the mainlist StreetList object before to pass in the session, but no time work this out,
    # and probably not sensible approach anyway?
    # json_main = flask.jsonify(list=mainlist.serialize())
    # flask.session['mainlist'] = json_main
    # flask.session['sidelist'] = sidelist
    return redirect(url_for('.load_streetlist', street=street, number=number, c1=c1, c2=c2, c3=c3))

@street_list_blueprint.route('/<string:street>/<number>/<c1>/<c2>/<c3>', methods=['POST', 'GET'])
def load_streetlist(street, number, c1, c2, c3):
    mainlist = Lists.StreetList.get_mainlist(street, number)  # first StreetList object
    sidelist = Lists.StreetList.get_clist(c1, c2, c3)  # second StreetList object if any Box C streets needed
    return render_template('street_lists/street_list.jinja2', mainlist=mainlist, sidelist=sidelist, number=number, street=street)

    #iterate mainlist and sidelist objects in the template following Jose's Udemy tutorial item example
