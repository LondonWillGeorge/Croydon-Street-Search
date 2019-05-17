# import pymongo
# import dateutil

from Source.common.database import Database
from Source.common.utils import NumRange, post_dist
# from bson.objectid import ObjectId

import datetime
# from datetime import datetime
# from dateutil import tz

# Do we need the date field auto-generated in the URL? Would be simpler without it.
# Like this, each time you bring up the report as GET request, it will change report time to current time.
# Then bringing up actual reports saved can be a different thing, with different URL using a Report ID.
# Surely would need to implement logins to do that anyway...?
# Later, can have function to save StreetReport object to a separate Mongo Reports collection,
# and Street Reports button on page will show list of reports made by current user.

# Remember if underlying street data changes later,
# reloading the same StreetReport object could produce a different report.

# A street report has properties of a title, the main street blurb, the side street blurbs, a date!
# Also a reference number property which is entered in a textbox, and any other comments, entered in another
# textbox.
# On street report page, these all display as ready to print, it is final page in the app as at 6-10-2017.


# pass dummy status of main and c1 to 3 to this class?
class StreetReport(object):
    def __init__(self, title, maintext, side1text=None, side2text=None, side3text=None, datestring=None,
                 maindummy=False, side1dummy=False, side2dummy=False, side3dummy=False, ref="", comments=""):
        self.title = title
        self.maintext = maintext
        self.side1text = side1text
        self.side2text = side2text
        self.side3text = side3text
        self.datestring = datestring
        self.maindummy = maindummy
        self.side1dummy = side1dummy
        self.side2dummy = side2dummy
        self.side3dummy = side3dummy
        self.ref = ref
        self.comments = comments

    # .maintained method takes a street record dictionary as argument.
    # doesn't use any class or instance attributes, therefore we can make it a static method.
    @staticmethod
    def maintained(strt):
        if strt["Adoption Status"] == "Adopted":
            if strt["Road Class"] == "TFL":
                maintained_by = "is a road section maintained at public expense by Transport for London."
            else:
                maintained_by = "is a road section maintained at public expense by The London Borough of Croydon."
        else:
            maintained_by = "is a privately maintained road."

        # Road Number eg A23, A232 etc. it is included only for the larger roads in the database
        # Major roads like A23 are often TFL maintained or London Distributor roads etc. so important to know
        roadnum = strt["Road Number"]
        if roadnum is not None and roadnum != "" and roadnum != "None":
            maintained_by += "\nThis road is numbered as the " + roadnum + " at this section."

        return maintained_by

    # called by main_text method in this class, to reduce its (McCabe) complexity.
    @staticmethod
    def add3questions(extra_info, main_string):
        # if there is no street in Three_Questions collection with this street and district name,
        # extra_info will return None.
        if extra_info is not None:
            if extra_info["TfL Side Road"] == 1:
                main_string += "\n This road is a Side Road to a TfL Road"
                if extra_info["Road1"] != "":
                    main_string += ", which is the " + extra_info["Road1"] + " at this point."
                else:
                    main_string += "."

            if extra_info["Borough Boundary"] == 1:
                main_string += "\nPart of this road section is under the authority of " + extra_info["Borough1"]
                if extra_info["Borough2"] != "" and extra_info["Borough2"] != "None":
                    main_string += ", and another part under the authority of " + extra_info["Borough2"] + "."
                else:
                    main_string += "."

            if extra_info["Split"] == 1:
                main_string += "\nThis road section has a split status as " + extra_info["Split As"] + "."
        else:
            main_string += " This road section is not a TfL Side Road, does not cross another council's boundary, " \
                           "and doesn't have any split status."
        return main_string

    # This method uses .maintained method of this class, so should be a class method.
    # stringified str() street and district fields, to avoid getting int not str error for district "16" etc.
    @classmethod
    def main_text(cls, main, namenum):
        main_street = str(main["Street"])
        main_district = str(main["District"])
        long_district = post_dist(main_district)
        propnum = str(namenum)
        if propnum == "--":
            report_title = "(No property name or number given) " + main_street + ", " + long_district
        else:
            report_title = propnum + " " + main_street + ", " + long_district

        # Due to funny way data copied at moment, below query needs to be a bit more complicated.
        # Would need to clean up underlying Mongo collection, then can simplify below and avoid slight expensive regex.
        # Or better still, just join collections together with the street and district fields.
        try:
            dist_or_integer = int(main_district)
        except (ValueError, TypeError):
            dist_or_integer = main_district

        extra_info = Database.find_one("Three_Questions",
                                       {"Street": {'$regex': main_street},
                                        "District": {'$in': [dist_or_integer, str(main_district), ""]}})
        # was: extra_info = Database.find_one("Three_Questions", {"Street": main_street, "District": main_district})

        # main_string and extra_info compose text strings to show on the report page, according to
        # content of the returned data on chosen street(s) from Mongo.
        mainrange = NumRange(main).range

        main_string = main_street + ", " + long_district + ", "

        if mainrange == "All numbers":
            main_string += "for all property numbers in the section of the road in this district, " +  \
                           cls.maintained(main)
        else:
            main_string += "in the section from " + mainrange + ", " + \
                      cls.maintained(main)

        main_string = cls.add3questions(extra_info, main_string)

        return report_title, main_string

    # Composes text string for each Box C side street which is shown on report.
    # takes a street record dictionary 'side' as argument.
    # Uses .maintained method of the class, therefore made it a class method.
    # Needed to stringify str() street and district variables, otherwise eg District '19' crashes with int not str error
    @classmethod
    def c_text(cls, side):
        c_street = str(side["Street"])
        c_district = str(side["District"])
        c_longdist = post_dist(c_district)
        if side is not None:
            c_string = c_street + ", " + c_longdist + ", " + cls.maintained(side) + "\n"

            if any(x in {"Class A", "Class B", "Class C"} for x in side["Road Class"]):
                c_string += " This road section is a " + side["Road Class"] + " road, and the length is "
            elif side["Road Class"] == "Service Road":
                c_string += " This road section is a Service Road, and the length is "
            else:
                c_string += " This road section is Unclassified, and the length is "

            # 'Length of Street' is a float type in Mongo!
            # So below convert to integer, then to string, then can concatenate.
            c_string += str(int(side["Length of Street"])) + " metres."
            try:
                dummyside = side["Dummy"]
            except (KeyError, ValueError, TypeError, NameError):
                dummyside = False
            return c_string, dummyside
        else:
            return "", False

    # create_report method queries Mongo again, using my custom sequenced ID numbers,
    # to return the street info for this report.

    # mainselection is my custom created Mongo ID field number for the main street,
    # side1, side2, side3 are same ID numbers for any side streets 1 2 3,
    # namenum is string representing the property name or number, which user entered on the first search page.

    # 25-9-17 changed search to query on id field which I have created, not Mongo default _id ObjectId field.
    # So shorter RESTful type URLs can be produced, using this id field.
    # NB mainselection is a string value when it comes in, so int() convert to integer for query to run.
    @classmethod
    def create_report(cls, mainselection, side1, side2, side3, namenum):
        # was: Main = Database.find_one("Highways_Register", ObjectId(mainselection))
        # maindum shows if street is dummy or real.
        main = Database.find_one("Highways_Register", {"id": int(mainselection)})
        report_title, main_string = cls.main_text(main, namenum)
        try:
            maindum = main["Dummy"]
        except (KeyError, ValueError, TypeError, NameError):
            maindum = False
        # Below initializes 2 arrays to produce 0 to 3 street record dictionaries,
        # corresponding to sideselection parameter.
        # I could do it with 1 array, but this would be less readable perhaps?
        # sidedummy is dummy street field to show if street is real or dummy one.
        c = ["", "", ""]
        sidetext = ["", "", ""]
        sidedummy = [False, False, False]
        sidedict = {0: side1, 1: side2, 2: side3}

        # was: c[ind] = Database.find_one("Highways_Register", ObjectId(sidedict.get(ind)))

        # retrieves info from Mongo on 0 to 3 side streets user has chosen, using their ID numbers side1 side2 side3.
        for ind in range(3):
            if sidedict.get(ind) != "--":
                c[ind] = Database.find_one("Highways_Register", {"id": int(sidedict.get(ind))})
                sidetext[ind], sidedummy[ind] = cls.c_text(c[ind])
            else:
                sidetext[ind] = ""
        # should end up with size 3 array: sidetext, to return to the webpage.

        # Time problem! At moment, time shown is 1 hour behind DST UK summer time, UTC actually.

        # Tried to use TZ Olson Database API to Auto-detect time zones:
        # from_zone = tz.tzutc()
        # to_zone = tz.tzlocal()
        # utc = datetime.utcnow()
        # # Tell the datetime object that it's in UTC time zone since datetime objects are 'naive' by default
        # utc = utc.replace(tzinfo=from_zone)
        # # Convert time zone
        # date = utc.astimezone(to_zone)

        # above TZ code from Stack Overflow still producing wrong time when run on server.
        # when run on my local computer, does produce correct time, so using hack below add 1 hour for UK DST time!
        date = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

        date_string = "Report time is " + date.strftime("%I:%M%p") + " on " + date.strftime("%A %d %B %Y")

        return cls(report_title, main_string, sidetext[0], sidetext[1], sidetext[2], date_string,
                   maindum, sidedummy[0], sidedummy[1], sidedummy[2])

    def save_to_mongo(self):
        # save to a Reports collection in Mongo, including the date here!
        # Do we want generate a Report_id as UUID?
        # can follow jslvtr's way of doing this, which also needs a json method?
        pass

# some old code below for interest sake:
        # C_count = len(sideselection)

        # .get built-in method, equivalent of select case method in VBA
        # current_side = {0: sideselection[0], 1: sideselection[1], 2: sideselection[2]}.get(index)
        #  , "" .get default not needed within this narrow usage?
        #
        # if current_side is not None:
        #     boxC_strings.append(StreetReport.c_streets(current_side))
        # else:
        #     break

        # loop 3 times:
        # if length array >= current index,
        # set new array by doing method on array this index.
        # otherwise set variable to None, no need to exit loop at all!

# testing....
# Database.initialize()
# m = Database.find_one("Highways_Register", {"Street": "BRIGHTON ROAD", "District": "SC"})
# c1 = Database.find_one("Highways_Register", {"Street": "FARQUHARSON ROAD"})
# c2 = Database.find_one("Highways_Register", {"Street": "PORTNALLS ROAD"})  # class C
# c3 = Database.find_one("Highways_Register", {"Length of Street": 530, "District": "CL"})  # should be Service Road 14
# StreetReport(m, 123, c1, c2, c3).create_report()
