from Source.common.database import Database
from Source.common.utils import NumRange, post_dist

# for entering a new street into the database
# (dummy at the moment, so 'dummy' property defaults to true)
# onb to ene fields are for the odd and even street numbers which delineate this 'street section'
class Street(object):
    def __init__(self, ID, street, district, long_dist, dummy=True, onb=None, one=None, enb=None, ene=None,
                 adoption=None, rdclass=None, length=None, road_no=None, has_tfl=None, tfl_rd=None, cross_boro=None,
                 boro1=None, boro2=None, is_split=None, split=None):
        self.id = ID
        self.dummy = dummy
        self.street = street
        self.district = district
        self.long_dist = long_dist
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

    @classmethod
    def save_to_mongo(cls):
        pass