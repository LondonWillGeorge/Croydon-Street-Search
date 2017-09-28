from Source.common.database import Database
from Source.common.utils import NumRange, post_dist


class DigOnly(object):
    def __getitem__(self, string_ordinal):
        ascii_0to9 = {48: '0', 49: '1', 50: '2', 51: '3', 52: '4', 53: '5', 54: '6', 55: '7', 56: '8', 57: '9'}
        return ascii_0to9.get(string_ordinal)

# Made ID default to None, which in fact means an empty streetlist, or no streetlist returned if you like.
# if ID has no default, then a null result on street search will cause WSGI long error message, not what we want.
# list_length property is integer count of number of streets in the list.
# The other properties are all arrays of this length, each corresponding to a field in Mongo collection.
# ID property is array of each of the Mongo ObjectIds for the streets in this list.
# long_dist is the full name of Postal District, obtained using the utils .post_dist method.
class StreetList(object):
    def __init__(self, ID=None, list_length=0, street=None, district=None, long_dist=None, numrange=None, adoption=None, rdclass=None, length=None,
                 road_no=None, has_tfl=None, tfl_rd=None, cross_boro=None, boro1=None, boro2=None,
                 is_split=None, split=None):
        self.id = ID
        self.list_length = list_length
        self.street = street
        self.district = district
        self.long_dist = long_dist
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

    # 20-9-17 this method not used, but leave in case future use, created to try to make this object JSON serializable,
    # so it could be passed in the Flask session variable. But maybe that is bad approach anyway.
    def serialize(self):
        return {
        'id': self.id,
        'list_length': self.list_length,
        'street': self.street,
        'district': self.district,
        'long_dist': self.long_dist,
        'numrange': self.numrange,
        'adoption': self.adoption,
        'rdclass':self.rdclass,
        'length': self.length,
        'road_no': self.road_no,
        'has_tfl': self.has_tfl,
        'tfl_rd': self.tfl_rd,
        'cross_boro': self.cross_boro,
        'boro1': self.boro1,
        'boro2': self.boro2,
        'is_split': self.is_split,
        'split': self.split
        }

    @classmethod
    def populate_list(cls, st_list):
        list_length = len(st_list)
        ID, street, district, long_dist, numrange, adoption, rdclass, length, road_no, has_tfl, tfl_rd, cross_boro, boro1, boro2, \
        is_split, split = [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []

        # 25-9-17 changed id property to append the id field from Highways_Register collection,
        # NOT the Mongo _id field. The id field is one I added by running a Javascript function in Mongo shell.
        # It increments by 1 for each record, and it needs a separate counter sequence value stored in a
        # collection in this Mongo database called "High_Reg_Counter".
        # st_list..["id"] seems to return the field as floating point value, so convert to integer with int().
        for ind in range(list_length):
            ID.append(int(st_list[ind]["id"]))
            street.append(st_list[ind]["Street"])
            district.append(st_list[ind]["District"])
            dist_name = post_dist(st_list[ind]["District"])
            long_dist.append(dist_name)
            numrange.append(NumRange(st_list[ind]).range)
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

        return cls(ID, list_length, street, district, long_dist, numrange, adoption, rdclass, length, road_no, has_tfl, tfl_rd,
                   cross_boro, boro1, boro2, is_split, split)

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
                    return cls()
            else:
                return cls()

        except:
            mainlist = [street for street in Database.find("Highways_Register",
                                                           {"Street": {'$regex': streetpart, '$options': 'i'}})]
            if len(mainlist) == 0:
                return cls()

        return cls.populate_list(mainlist)

    @classmethod
    def get_clist(cls, side1, side2, side3):
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

        return cls.populate_list(tight_sidelist)