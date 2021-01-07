import pymongo


class MongoHelper:
    def __init__(self, db_name):
        self.mongoUrl = "mongodb://localhost:27017"
        self.dbName = db_name
        self.mongoClient = pymongo.MongoClient(self.mongoUrl)
        self.mongoDb = self.mongoClient[self.dbName]

    def insertOne(self, collection, event_data):
        event = self.mongoDb[collection]
        result = event.insert_one(event_data)
        print(f'One post: {result.inserted_id}')

    def insertMany(self, collection, event_data_list):
        event = self.mongoDb[collection]
        result = event.insert_many(event_data_list)
        print(f'One post: {result.inserted_ids}')

    def findOne(self, collection, params):
        # single document
        return self.mongoDb[collection].find_one(params)

    def findMany(self, collection, params):
        # document list
        return self.mongoDb[collection].find(params)

    def deleteOne(self, collection, params):
        self.mongoDb[collection].delete_one(params)

    def deleteMany(self, collection, params):
        self.mongoDb[collection].delete_many(params)
