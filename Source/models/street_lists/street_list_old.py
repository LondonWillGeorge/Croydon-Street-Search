from Source.common.database import Database
from Source.common.utils import NumRange
import uuid

# Not needed so far - import re
# from Source.models.street_properties.street_property import StreetProperty

# We don't need json repr method to GET the streetlist from Mongo
# this object's properties are NOT the equivalent of a specific collection in Mongo
# and no need to SAVE the streetlist anyway, so no json method needed for this object.

# DigOnly is used with .translate standard Python method to extract only numerals from a string
# used eg if user types 321A for a house number, (or even 'sgrgre3sg2afsf1' !), it returns 321,
# which we can then check against number range for street section.


class DigOnly(object):
    def __getitem__(self, string_ordinal):
        ascii_0to9 = {48: '0', 49: '1', 50: '2', 51: '3', 52: '4', 53: '5', 54: '6', 55: '7', 56: '8', 57: '9'}
        return ascii_0to9.get(string_ordinal)

# create TRUE list object here while iterating streets, with properties Jinja can access, including range?
# refactor street_list as street_Query
# Street Array Object SAO, a variable size array, each item in array has properties Street, District, NumRange
# and perhaps all the other field properties from both collections??
# In Jinja, street[0].street, street[1].district, street[2].range  can do this???
# logic shouldn't be handled in the Jinja template! Find a way do it in the url_for method or in passing each
 # item in array to the template as separate object?! or something like this?

# we want main and c together as one object to get a consecutive ID or UUID to save it?
# in this case, one super-object has 2 arrays in it, plus the street name/number, ie 3 properties....?
# and each list has the range and all the fields as properties?!?!!!??
# so in the Jinja we get for street in list.mainlist show street.street, street.range etc.
# but they are arrays, each item in the array has same properties....!
# so set up the properties for each item in the array in __init__ method?
# Or StreetArray has street1, street2 etc properties. Street is an object, Does StreetArray have or need init method?
# or not, just get 2 streetlist objects one for main one for C..?

# or don't define properties in init, define them iteratively later on..? but then can't use class method?

# put listid=uuid on the streetlist object with main, clist and num.
# But need to save this to mongo if we want to re-use it and retrieve page?
# get_list main and Clist methods return the class, which is an array of street fields, plus the range field
# list_length is an integer, the number of streets in the result list.
# the other parameters (ie properties) like street, district are all ARRAYS of size list_length
# numrange corresponds to the number range for each 'street section', and the other properties
# match all the other fields from the two Mongo collections
# what if param is all none values eg tfl2? Then just supply None here, and if None, don't iterate in Jinja.
# NB numrange could easily be array with None values in some elements but not others.


class StreetList(object):
    def __init__(self, list_length, street, district, numrange=None, adoption=None, rdclass=None, length=None,
                 road_no=None, has_tfl=None, tfl_rd=None, cross_boro=None, boro1=None, boro2=None,
                 is_split=None, split=None):
        self.list_length = list_length
        self.street = street
        self.district = district
        self.numrange = numrange
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

        # or self.street now an array, access as street, can access this array later?
        # range(listlength) in jinja street[ind] etc.?

    @classmethod
    def get_mainlist(cls, streetpart, name_or_num=""):
        try:
            property_num = int(name_or_num.strip().translate(DigOnly()))
            super_mainlist = [street for street in Database.find("Highways_Register",
                                                             {"Street": {'$regex': streetpart, '$options': 'i'}})]
            mainlist = []
            if len(super_mainlist) > 0:
                for ind in range(len(super_mainlist)):

                    if NumRange(super_mainlist[ind]).in_range(property_num):
                        mainlist.append(super_mainlist[ind])
                if len(mainlist) == 0:
                    return None
            else:
                return None

        except:
        # no house number in this case, might be a name though
        # in either case, create street list without range condition

            mainlist = [street for street in Database.find("Highways_Register",
                                                           {"Street": {'$regex': streetpart, '$options': 'i'}})]
            if len(mainlist) == 0:
                return None

        cls.populate_list(mainlist)

    @classmethod
    def populate_list(cls, st_list):
        # now we have a mainlist object at this stage anyway!
        list_length = len(st_list)
        street, district, numrange, adoption, rdclass, length, road_no, has_tfl, tfl_rd, cross_boro, boro1, boro2, \
        is_split, split = [], [], [], [], [], [], [], [], [], [], [], [], [], []

        for ind in range(list_length):
            street.append(st_list[ind]["Street"])
            district.append(st_list[ind]["District"])
            numrange.append(NumRange(st_list[ind]).range)
            # numrange need to call the function here

            adoption.append(st_list[ind]["Adoption Status"])
            rdclass.append(st_list[ind]["Road Class"])
            length.append(st_list[ind]["Length of Street"])
            road_no.append(st_list[ind]["Road Number"])

            Check3qs = Database.find_one("Three_Questions", {"Street": street[ind], "District": district[ind]})
            if Check3qs is not None:
                has_tfl.append(Check3qs["TfL Side Road"])
                tfl_rd.append(Check3qs["Road1"])
                cross_boro.append(Check3qs["Borough Boundary"])
                boro1.append(Check3qs["Borough1"])
                boro2.append(Check3qs["Borough2"])
                is_split.append(Check3qs["Split"])
                split.append(Check3qs["Split As"])
            else:
                has_tfl.append(None)
                tfl_rd.append(None)
                cross_boro.append(None)
                boro1.append(None)
                boro2.append(None)
                is_split.append(None)
                split.append(None)


        # for each street in mainlist, check if there is 3questions record with this street and district name
        # if there is, iterate these fields into the array properties also.
        #iterate mainlist into the class properties here, and append 2nd collection fields

        # this works! return cls(number streets in the list, "arraystreet", "arraydistrict"...etc.)
        return cls(list_length, street, district, numrange, adoption, rdclass, length, road_no, has_tfl, tfl_rd,
                   cross_boro, boro1, boro2, is_split, split)

    @classmethod
    def get_clist(cls, side1, side2, side3):
        # query statement won't work with string expression or '+' operator, but below works for now anyway:
        if side1 is not None and side1.strip() != "":
            if side2 is not None and side2.strip() != "":
                if side3 is not None and side3.strip() != "":
                    sidelist = [street for street in Database.find("Highways_Register",
                                                                   {'$or': [{"Street": {'$regex': side1.strip(),
                                                                                        '$options': 'i'}},
                                                                            {"Street": {'$regex': side2.strip(),
                                                                                        '$options': 'i'}},
                                                                            {"Street": {'$regex': side3.strip(),
                                                                                        '$options': 'i'}}]})]
                else:
                    sidelist = [street for street in Database.find("Highways_Register",
                                                                   {'$or': [{"Street": {'$regex': side1.strip(),
                                                                                        '$options': 'i'}},
                                                                            {"Street": {'$regex': side2.strip(),
                                                                                        '$options': 'i'}}]})]
            else:
                sidelist = [street for street in Database.find("Highways_Register",
                                                               {"Street": {'$regex': side1.strip(),
                                                                           '$options': 'i'}})]
            tight_sidelist = []
            if len(sidelist) > 0:
                tight_sidelist.append(sidelist[0])
            if len(sidelist) > 1:
                for ind in range(1, len(sidelist)):
                    if not ((sidelist[ind]["Street"] == sidelist[ind-1]["Street"]) and
                            (sidelist[ind]["District"] == sidelist[ind-1]["District"])):
                        tight_sidelist.append(sidelist[ind])
        else:
            tight_sidelist = []

        cls.populate_list(tight_sidelist)

Database.initialize()
a = StreetList.get_mainlist("add")
if a is None:
    print ("No results!")
else:
    print(a.list_length, a.street, a.district, a.numrange, a.has_tfl, a.tfl_rd, a.boro1, a.split)
    for ind in range(a.list_length):
        print(a.boro1[ind])




#####################################

#     def get_from_mongo(self):
#         try:
#             property_num = int(self.name_or_num.strip().translate(DigOnly()))
#             print("House number with letters stripped is \"{}\"".format(property_num))
#
#             super_mainlist = [street for street in Database.find("Highways_Register",
#                                                            {"Street": {'$regex': self.streetpart, '$options': 'i'}})]
#
#             mainlist = []
#             if len(super_mainlist) > 0:
#                 for ind in range(len(super_mainlist)):
#
#                     if NumRange(super_mainlist[ind]).in_range(property_num):
#                         mainlist.append(super_mainlist[ind])
#
#             else:
#                 print("Sorry, no streets found with \"{}\" as part of the street name. Please check and try again."
#                       .format(self.streetpart.strip()))
#                 return None
#
#         except:
#         # no house number in this case, might be a name though
#             # in either case, create street list without range condition
#
#             mainlist = [street for street in Database.find("Highways_Register",
#                                                            {"Street": {'$regex': self.streetpart, '$options': 'i'}})]
#

#
#             # following checks if any duplicate entries where street and district same, eg for different
#             # number ranges on same street, and removes duplicates from Box C choice list.
#             # **At present, still doesn't remove if they are not adjacent in the data collection, eg Brighton Road CL
#             # did not remove duplicate. This is rare, and anyway duplicates in this list won't bother user much,
#             # they can choose either.

#
#         if len(mainlist) > 0:
#             for ind in range(len(mainlist)):
#                 print(mainlist[ind]["Street"], " ", mainlist[ind]["District"],
#                       " ", NumRange(mainlist[ind]).nums())
#
#             if len(tight_sidelist) > 0:
#                 print("\n********\nBox C Side street(s) as follows:\n********\n")
#                 for ind in range(len(tight_sidelist)):
#                     print(tight_sidelist[ind]["Street"], " ", tight_sidelist[ind]["District"])
#             else:
#                 print("No Box C streets found, please check if you need to and redo this search.")
#
#         else:
#             print("Sorry, no streets found with \"{}\" as part of the street name. Please check and try again."
#                   .format(self.streetpart.strip()))
#
#         # returns list of main street choices, and list of side street choices
#         # user chooses 1 main street, and 0 to 3 side streets to call the get method on StreetReport,
#         # which are index numbers on below objects.
#         # name_or_num variable will be needed for street report, pass to next page here, then to report.
#         return mainlist, tight_sidelist, self.name_or_num
        # don't need to return , self.list_id? You wouldn't want report with same id? Or would you?
        # if you brought up the list again and wanted make different choice, it would assign same id to new report

# For testing....

# Database.initialize()

# a = StreetList(input("Type bit of name?>>"), "fugincomplexID", input("Name or number?>>"),
#                           input("First Box C road name bitty titty?>>>"),
#                           input("Second Box C road name bitty titty?>>>"), input("3rd Box C road name bitty titty?>>>")).get_from_mongo()

# print(a)
# print(a[0],a[1],a[2])

# below FYI was Mongo string which works, very complex nesting, but found better way I think!

        # mainlist = [street for street in Database.find("Highways_Register",
        #             {"$and": [{"Street": {'$regex': streetpart, '$options': 'i'}},
        #                       {"$or": [{"$or": [{"Odd Number Beginning": {"$exists": False}}, {"Odd Number Beginning": 0}, {"Odd Number Beginning": ""}]},
        #                           {"$and": [{"$or": [{"Odd Number Beginning": {"$lte": property_num}}, {"Even Number Beginning": {'$lte': property_num}}]},
        #             {"$or": [{"Odd N umber Ending": {'$gte': property_num}},
        #             {"Even Number Ending": {'$gte': property_num}}]}]}]}]})]