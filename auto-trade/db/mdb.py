import pymongo


class MongoDbManager():
    # id, pwd 아직 안 씀
    def __init__(self, domain, db_name, port=27017):
        url = 'mongodb://{0}:{1}/'.format(domain, port)
        self.client = pymongo.MongoClient(url)
        self.db = self.client[db_name]
        self.init_collection()

    def get_table(self, table_name):
        return self.db[table_name]

    def find(self, table_name, query, filter=None):
        # query = {"address": "Park Lane 38"}
        table = self.get_table(table_name)
        if filter is None:
            return table.find(query)
        else:
            return table.find(query, filter)

    def add(self, table_name, data):
        table = self.get_table(table_name)
        if isinstance(data, (list)):
            if len(data) > 0:
                table.insert_many(data)
        elif isinstance(data, (dict)):
            table.insert_one(data)

    def edit(self, table_name, query, row):
        table = self.get_table(table_name)
        table.update_one(query, {"$set": row})

    def max(self, table_name, query, field):
        table = self.get_table(table_name)
        result = table.find(query).sort(field, -1).limit(1)
        results_count = result.count(True)
        # print(results_count)
        value = None
        if results_count == 0:
            value =None
        else:
            for x in result:
                value = x[field]
                break
        return value

    def min(self, table_name, query, field):
        table = self.get_table(table_name)
        return table.find(query).sort({field: -1}).limit(1)

    def init_collection(self):
        if "code" not in self.db.list_collection_names():
            self.get_table('code').create_index(
                [("date", pymongo.DESCENDING), ("code", pymongo.ASCENDING)],
                unique=True
            )

        if "stock_daily" not in self.db.list_collection_names():
            self.get_table("stock_daily").create_index(
                [("code", pymongo.ASCENDING), ("date", pymongo.DESCENDING)],
                unique=True
            )


if __name__ == "__main__":
    db = MongoDbManager('localhost', 'test')
    # db.add('company', {'code': '00000', 'value': 'test0'})
    # db.add('company', {'code': '00001', 'value': 'test1'})
    # db.add('company', [{'code': '00002', 'value': 'test1'}, {'code': '00003', 'value': 'test3'}])
    result = db.find('company', {'code': '00000'})
    list = []
    # { "address": { "$regex": "^S" } }
    for x in result:
        list.append(x)
    print(list)