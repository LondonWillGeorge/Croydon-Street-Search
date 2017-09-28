import pymongo


class Database(object):
    # static properties of every Database object
    URI = "mongodb://127.0.0.1:27017"
    DATABASE = None

# the main database is called CON29, collections are all under this, roughly
# equivalent to tables in a SQL relational database
    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client['CON29']

# At present, we want insert for users only, NOT for the street info!
    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)

# might want update and remove for users only, probably not for the street info
    # in this app!
    @staticmethod
    def update(collection, query, data):
        Database.DATABASE[collection].update(query, data, upsert=True)

    @staticmethod
    def remove(collection, query):
        return Database.DATABASE[collection].remove(query)
