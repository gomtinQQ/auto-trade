import pymongo


class MongoDbManager():
    # id, pwd 아직 안 씀
    def __init__(self, domain, db_name, port=27017):
        url = 'mongodb://{0}:{1}/'.format(domain, port)
        self.client = pymongo.MongoClient(url)
        self.db = self.client[db_name]

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
            table.insert_many(data)
        elif isinstance(data, (dict)):
            table.insert_one(data)

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