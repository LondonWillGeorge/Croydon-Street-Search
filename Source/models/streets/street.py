from Source.common.database import Database
from Source.common.utils import dist_code, post_dist


# The Three_Questions collection fields: has_tfl, cross_boro, is_split default to 0 ie no data here
# these are Boolean fields.
# note a consecutive ID field was created for Three_questions collection,
# but not used in other methods as at 13.10.17. So using same ID field as Highw_Register collection
# for Three_Questions collection, to keep it simpler, and aligned at least for any future expansion.
class Street(object):
    """for entering a new street into the database (dummy at the moment, so 'dummy' property defaults to true)
    onb to ene fields are for the odd and even street numbers which delineate this 'street section'"""
    def __init__(self, street, dist_number, dummy=True, visible=True, onb=None, one=None, enb=None, ene=None,
                 adoption=None, rdclass=None, length=None, road_no=None, has_tfl=0, tfl_rd=None, cross_boro=0,
                 boro1=None, boro2=None, is_split=0, split=None, i_d=None):
        if i_d is not None:
            self.id = i_d
        else:
            new_id = int(Database.find_one("High_Reg_Counter", {})['seq']) + 1
            self.id = new_id
        self.dummy = dummy
        self.visible = visible
        self.street = street
        # this converts the input form district number dist_number to short district code,
        # as previously used in database.
        self.district = dist_code(dist_number)
        # This converts the code to the long district name.
        self.long_dist = post_dist(self.district)
        self.onb = onb
        self.one = one
        self.enb = enb
        self.ene = ene
        self.adoption = adoption
        self.rdclass = rdclass
        self.length = length
        self.road_no = road_no
        self.has_tfl = has_tfl
        self.tfl_rd = tfl_rd
        self.cross_boro = cross_boro
        self.boro1 = boro1
        self.boro2 = boro2
        self.is_split = is_split
        self.split = split

    # first finds current value of counter collection, and adds 1 to this.
    # sets new_id of new dummy street to this number.
    # then calls JSON methods on this street, and uses Database.update method to save to Mongo.
    # could have used insert method instead, but update method includes upsert=True, so will insert or update.
    # This could help cover an error if the id number already exists for some reason.
    def save_to_mongo(self):
        # with counter update line following try except clause for creating the record,
        # this means the street counter will be incremented only if the street is successfully saved.
        try:
            Database.update("Highways_Register", {"id": self.id}, self.json1(self.id))
            Database.update("Three_Questions", {"ID": self.id}, self.json2(self.id))
        except TypeError:
            return """Somehow, a 'type error' has occurred. Sorry, if you have time to email the admin with any details
                   of the search you did to produce this error, we would be very very grateful! Please try again."""
        except (ValueError, NameError, RuntimeError, SyntaxError):
            return """Somehow, an error has occurred. Sorry, if you have time to email the admin with any details
                   of the search you did to produce this error, we would be very very grateful! Please try again."""
        Database.update("High_Reg_Counter", {"_id": "streets"}, {"seq": self.id})  # args: collection, query, data
        return "Congratulations! Your Dummy street, \"{0}\" has been created in the database." .format(self.street)
        # return self.id

    def json1(self, newid):
        return {
            "Dummy": self.dummy,
            "Visible": self.visible,
            "Street": self.street,
            "District": self.district,
            "Adoption Status": self.adoption,
            "Road Class": self.rdclass,
            "Length of Street": self.length,
            "Odd Number Beginning": self.onb,
            "Odd Number Ending": self.one,
            "Even Number Beginning": self.enb,
            "Even Number Ending": self.ene,
            "Road Number": self.road_no,
            "id": newid
        }

    def json2(self, newid):
        return {
            # Mongo should auto generate its own _id? don't want "_id": self._id,
            "Dummy": self.dummy,
            "Visible": self.visible,
            "ID": newid,
            "Street": self.street,
            "District": self.district,
            "TfL Side Road": self.has_tfl,
            "Road1": self.tfl_rd,
            "Borough Boundary": self.cross_boro,
            "Borough1": self.boro1,
            "Borough2": self.boro2,
            "Split": self.is_split,
            "Split As": self.split
             }

    # for dummy streets already entered, this method can be invoked to change Visible property to false
    # for this demo app, I want to do this instead of actually deleting the street from database.
    # If Visible is false, then this street should not be displayed in any searches.
    @classmethod
    def hide_street(cls, streetid):
        Database.update("Highways_Register", {"id": streetid}, {"Visible": False})
        Database.update("Three_Questions", {"ID": streetid}, {"Visible": False})

    # If all the dummy streets can be displayed on one screen, any hidden ones can be reshown with this method.
    @classmethod
    def show_street(cls, streetid):
        Database.update("Highways_Register", {"id": streetid}, {"Visible": True})
        Database.update("Three_Questions", {"ID": streetid}, {"Visible": True})
