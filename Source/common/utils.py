
# common utility functions used by this application
#
# Function email_is_valid validator uses Regular Expressions language, importing
# library for this below called re. This library built in Python no need to install.
# In regex language, ^ $ are begin end, means analyse whole string which user inputs.
# [] means any number characters I think
# [\w-] means any number characters including hyphen, which is excluded otherwise for some
# reason. @ means @. \. means . as this needs to be escaped. () means repeat any number of times.
# QED from above '^[\w-]+@([\w-]+\.)+[\w]+$' regex string
# gives a proper email format. NB will_crox@hu.ie.dh-hye.?:OPEE%$£.feg.com for example
# would be accepted here, but no need to be any more pedantic than this!

from passlib.hash import pbkdf2_sha512
import re
from flask import request, url_for


# Used to convert short District code saved in Mongo district field into the full name of the Postal District
# .get method defaults to 'Croydon' with any unknown or blank values in database.
def post_dist(district):
    dist_codes = {"CL": "Coulsdon CR5", "PR": "Purley CR8", "25" and 25: "London SE25", "16" and 16: "London SW16",
                  "19" and 19: "London SW19", "BE": "Beckenham BR3", "KN": "Kenley CR8", "SC": "South Croydon CR2",
                  "TH": "Thornton Heath CR7", "WA": "Warlingham CR6", "WH": "Whyteleafe CR3"}
    return dist_codes.get(district, "Croydon (CR0, CR2, CR7 or CR9)")


# this kind of reverse of post_dict, used when new street created, user chooses the full district name,
# and this returns number from the form, passed here, which then gives short code for saving in the database.
# NB originally to invert this dictionary quick courtesy of SO did: inv_map = {v: k for k, v in Dist_Codes.items()}
def dist_code(distnum):
    longdistricts = {'1': 'CL', '2': 'PR', '3': 25, '4': 16, '11': 19,
                     '10': 'BE', '5': 'KN', '6': 'SC', '7': 'TH',
                     '8': 'WA', '9': 'WH'}
    return longdistricts.get(distnum, "CR")


# In the NumRange init method, argument passed to street_section must be one dictionary record
# in Highways_Register collection, so it should have all the named fields.
class NumRange(object):
    def __init__(self, street_section):
        try:
            self.onb = int(street_section["Odd Number Beginning"])
            self.one = int(street_section["Odd Number Ending"])
            self.enb = int(street_section["Even Number Beginning"])
            self.ene = int(street_section["Even Number Ending"])
            if min(self.onb, self.one, self.enb, self.ene) > 0:
                self.range = str(self.onb) + " to " + str(self.one) + " Odds, and " + str(self.enb) + " to " \
                 + str(self.ene) + " Evens"
            else:
                self.range = "All numbers"
        except (ValueError, TypeError):
            self.range = "All numbers"

    # pass property_num integer as the argument here, MUST be an integer passed anyway,
    # default number=0 to accommodate possible future errors if application is expanded.
    # if ANY of the number fields fail init try method, the init except triggers, so self.onb is None
    # (so is self.one, enb and ene, so we only need to check one of them!),
    # in which case we assume this road section applies for all numbers, so we let this query onto the list.
    def in_range(self, number=0):
        try:
            range_boolean = (number >= self.onb or number >= self.enb) and (number <= self.one or number <= self.ene)
        except (TypeError, ValueError):
            range_boolean = True
        return range_boolean

    # def nums(self):
    #     return self.range


class Utils(object):

    @staticmethod
    def maintained(street):
        # if we want to move this method to common file here?
        pass

    @staticmethod
    def email_is_valid(email):
        email_address_matcher = re.compile('^[\w-]+@([\w-]+\.)+[\w]+$')
        return True if email_address_matcher.match(email) else False

    @staticmethod
    def hash_password(password):
        """
        Hashes a password using pbkdf2_sha512
        :param password: The sha512 password from the login/register form
        :return: A sha512->pbkdf2_sha512 encrypted password
        """
        return pbkdf2_sha512.encrypt(password)

        # Checks that the password the user sent matches that of the database.
        # The database password is encrypted more than the user's password at this stage.
        # # Will's comment: pbkdf2 produces a DIFFERENT hash each time the function
        # # is applied to the SAME SHA512 hash of one password.
        # # In contrast, SHA512 always hashes same password to same value,
        # # so SHA512 return value of all passwords up to certain length have been hacked
        # # and freely available on Internet.
        # :param password: sha512-hashed password
        # :param hashed_password: pbkdf2_sha512 encrypted password
        # :return: True if passwords match, False otherwise

    @staticmethod
    def check_hashed_password(password, hashed_password):

        return pbkdf2_sha512.verify(password, hashed_password)

    # from Flask pocoo docs and SO answer which embellished this, default URL set to home function i.e. / root route!
    # this can be called with argument of page you want to redirect to.
    def redirect_url(bluep_fn_name='home'):
        return request.args.get('next') or \
               request.referrer or \
               url_for(bluep_fn_name)
