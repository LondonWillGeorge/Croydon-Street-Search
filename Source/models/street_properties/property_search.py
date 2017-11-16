
# ************ NOT NEEDED, EARLY TRY KEPT FOR HISTORICAL RECORD ONLY OF WRONG STRUCTURE IDEA **************************

# # This seems same as StreetList for now
# # not sure if it could be useful....
#
# # user inputs text arguments, but this can just call StreetList.get_from_mongo directly now
# # same parameters as here....
# from Source.models.street_lists.street_list import StreetList
#
#
# class PropertySearch(object):
#     def __init__(self, streetpart, name_or_num="", side1=None, side2=None, side3=None):
#         self.streetpart = streetpart
#         self.name_or_num = name_or_num
#         self.side1 = side1
#         self.side2 = side2
#         self.side3 = side3
#
# # this Python builtin method gives string representation of object,
# # so eg the statements search = PropertySearch(..); print (search) will call this method
#     def __repr__(self):
#         property_repstring = "A search for a street with {} in its name".format(self.streetpart)
#         if self.name_or_num != "":
#             property_repstring = "A search for a property numbered/named \"{}\" on a street with \"{}\" in its name".format(self.name_or_num, self.streetpart)
#         if self.side1 is not None:
#             property_repstring += ", with a Box C street with \"{}\" in its name".format(self.side1)
#         if self.side2 is not None:
#             property_repstring += ", and a second Box C street with \"{}\" in its name".format(self.side2)
#         if self.side3 is not None:
#             property_repstring += ", and a third Box C street with \"{}\" in its name".format(self.side3)
#         property_repstring += "."
#         return property_repstring
#
#     # trying to return Mainlist class object ARRAY itself, and if any C streets, also the Clist class object ARRAY.
#     # NB clist may still come out as blank or None, if no C streets come from the user's search,
#     # as could mainlist of course.
#     def get_streetlist(self):
#         if all(side in [None, ""] for side in [self.side1, self.side2, self.side3]):
#             return StreetList.get_mainlist(self.streetpart, self.name_or_num), None, self.name_or_num
#         else:
#             return StreetList.get_mainlist(self.streetpart, self.name_or_num), \
#                    StreetList.get_clist(self.side1, self.side2, self.side3), self.name_or_num
#
#     # better if both these objects return array of records with all the fields plus the range from Mongo
#     # then report can access the class object, and retrieve different properties as needed for display.
#     # def get_mainlist(self):
#     #     return StreetList.get_mainlist(self.streetpart, self.name_or_num)
#     #
#     # def get_clist(self):
#     #     return StreetList.get_clist(self.side1, self.side2, self.side3)
