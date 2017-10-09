from flask import Flask, render_template
from Source.common.database import Database
import uuid

from Source.models.street_reports.views import street_report_blueprint
from Source.models.users.views import user_blueprint
from Source.models.street_lists.views import street_list_blueprint
# from Source.models.street_reports.views import street_report_blueprint

__author__ = "Will Croxford, with some base structure elements based on Github: jslvtr, \
from a different tutorial web application for online price scraping."

app = Flask(__name__)
app.config.from_object('Source.config')

#***********************
# Use uuid.hex to generate secret key, Blank out secret key before sending anyone source code!
app.secret_key = "75c6cf2c458d45bb9603c2cece827920"
#***********************

app.register_blueprint(user_blueprint, url_prefix="/users")
app.register_blueprint(street_list_blueprint, url_prefix="/streetlists")
app.register_blueprint(street_report_blueprint, url_prefix="/streetreports")

@app.before_first_request
def init_db():
    Database.initialize()



@app.route('/')
def home():
    return render_template('home.jinja2', list_id=uuid.uuid4().hex)

@app.route('/about.jinja2')
def about():
    return render_template('about.jinja2')

@app.route('/Hacker_Solution.jinja2')
def hacker():
    return render_template('Hacker_Solution.jinja2')
