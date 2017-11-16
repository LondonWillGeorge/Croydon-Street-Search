# In this model, views.py files are the Flask Blueprint for this object.
# ie they describe what HTTP API endpoints are associated to objects of this class.
from flask import Blueprint, render_template, request, redirect, url_for
import Source.models.street_reports.street_report as Report

__author__ = 'Will Croxford'

street_report_blueprint = Blueprint('street_reports', __name__)


# sideselection array has 0 to 3 length. Assume here for now max. 3 length.
# at moment if more than 3 streets selected, iterates over first 3.
@street_report_blueprint.route('/<string:number>', methods=['POST', 'GET'])
def get_streetreport(number):
    # gets my custom sequential ids of radio and any checkboxes selected, NB best to leave original Mongo IDs in place!
    mainselection = request.form['MainlistRadios']
    # control for nothing selected in lists already done with JS client side validation.
    sideselection = request.form.getlist('SidelistCheckboxes')

    # if we try sending sideselection array variable to the route, somehow this doesn't work, gives BSON error
    # after adding funny characters to field, like [//'.......//'] where .... is original ObjectId
    side = ["--", "--", "--"]
    for index in range(3):
        if len(sideselection) >= (index + 1):
            side[index] = sideselection[index]

    # should end up with length 3 array side, to pass to page, if no C street, sets to '--' for the URL.

    return redirect(url_for('.load_streetreport', mainselection=mainselection, side1=side[0], side2=side[1],
                            side3=side[2], number=number))


# 2nd method to put variables in URL here, call create_report in 2nd method not first!
@street_report_blueprint.route('/HouseNo:<string:number>/Street:<mainselection>/BoxC:<side1>/BoxC:<side2>/BoxC:<side3>',
                               methods=['POST', 'GET'])
def load_streetreport(mainselection, side1, side2, side3, number):
    # report is a StreetReport object, whose properties will be accessed in Jinja.
    report = Report.StreetReport.create_report(mainselection, side1, side2, side3, number)
    return render_template('street_reports/street_report.jinja2', report=report)

    # gave up trying to pass object in the session variable for now, could be bad approach also.
    # mainlist = flask.session['mainlist']
    # sidelist = flask.session['sidelist']

    # Do we need a try except clause for sideselection?

# maybe simplest try passing variables in url_for in Jinja template separated by ,
# which gets them all appended as queries to the URL, if we need to make the URL unique to the queries?

# check Jose chair application how to return exit function, (break is for loops only) and handle errors?

# Show previous streetlist and streetreport selections as lines on these pages, iterated from the collection,
# maybe need implement user login to do this, or can we do with just a session variable for now?

# And a trial method to insert new street on homepage? Message to tell people try and find your new street here?

# below works to generate UUID, but silly as need to pass other variables all in the URL also.
# This was my initial misunderstanding how dynamic URLs work.
# maybe do need session variable to store UUID somehow
# @street_report_blueprint.route('/', methods=['POST','GET'])
# def get_streetreport(reportid=uuid.uuid4().hex):
#     mainselection = request.form['MainlistRadios']
#     return redirect(url_for('.get_reportpage', reportid=reportid, mainselection=mainselection))
#
# @street_report_blueprint.route('/<string:reportid>/<string:mainselection>', methods=['POST', 'GET'])
# def get_reportpage(reportid, mainselection):
#
#     return render_template('street_reports/street_report.jinja2', reportid=reportid, mainselection=mainselection)
