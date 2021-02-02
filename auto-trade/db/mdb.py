import pymongo
from datetime import datetime


class MongoDbManager():
    # id, pwd 아직 안 씀
    def __init__(self, domain, db_name, port=27017):
        url = 'mongodb://{0}:{1}/?compressors=snappy'.format(domain, port)
        self.client = pymongo.MongoClient(url)
        self.db = self.client[db_name]
        self.init_collection()

    def add_table(self, table_name):
        self.db.create_collection(table_name, storageEngine={'wiredTiger': {'configString': 'block_compressor=snappy'}})

    def get_table(self, table_name):
        return self.db[table_name]

    def find(self, table_name, query, filter=None):
        # query = {"address": "Park Lane 38"}
        table = self.get_table(table_name)
        find_result = None
        if filter is None:
            find_result = table.find(query)
        else:
            find_result = table.find(query, filter)

        if find_result:
            find_result = list(find_result)
        for x in find_result:
            if x['_id']:
                del x['_id']
        return find_result

    def add(self, table_name, data):
        table = self.get_table(table_name)
        # if isinstance(data, (list)):
        if isinstance(data, list):
            size = len(data)
            if size > 0:
                table.insert_many(data)
                # for i in range(0, size, 100):
                #     table.insert_many(data[i: i + 100 if i + 100 < size else size])
        elif isinstance(data, dict):
            table.insert_one(data)

    def edit(self, table_name, query, row):
        table = self.get_table(table_name)
        table.update_one(query, {"$set": row})

    def remove(self, table_name):
        table = self.get_table(table_name)
        table.remove()

    def max(self, table_name, query, field):
        table = self.get_table(table_name)
        result = table.find(query).sort(field, -1).limit(1)
        results_count = result.count(True)
        # print(results_count)
        value = None
        if results_count == 0:
            value = None
        else:
            for x in result:
                value = x[field]
                break
        return value

    def min(self, table_name, query, field):
        table = self.get_table(table_name)
        return table.find(query).sort({field: -1}).limit(1)

    def count(self, table_name, query={}):
        table = self.get_table(table_name)
        return table.count(query)

    def page(self, table_name, page, size, query={}, sort=None):
        table = self.get_table(table_name)
        find_result = table.find(query).skip((page - 1) * size).limit(size) if sort is None else table.find(query).sort(
            sort).skip((page - 1) * size).limit(size)
        if find_result:
            find_result = list(find_result)
        for x in find_result:
            if x['_id']:
                del x['_id']
        return find_result

    def dist(self, table_name, column, query={}):
        table = self.get_table(table_name)
        return table.find(query).distinct(column)

    def init_collection(self):
        if "code" not in self.db.list_collection_names():
            self.add_table("code")
            self.get_table('code').create_index(
                [("date", pymongo.DESCENDING), ("code", pymongo.ASCENDING)],
                unique=True
            )

        if "stock_daily" not in self.db.list_collection_names():
            self.get_table("stock_daily").create_index(
                [("code", pymongo.ASCENDING), ("date", pymongo.DESCENDING)],
                unique=True
            )
        if "stock_daily_record" not in self.db.list_collection_names():
            self.get_table("stock_daily_record").create_index(
                [("date", pymongo.DESCENDING), ("code", pymongo.ASCENDING)],
                unique=True
            )
        if "stock_real" not in self.db.list_collection_names():
            self.get_table("stock_real").create_index(
                [("code", pymongo.ASCENDING), ("time", pymongo.DESCENDING)],
                unique=True
            )
        if "stock_yf_daily" not in self.db.list_collection_names():
            # self.add_table("stock_yf_daily_1030")
            self.get_table("stock_yf_daily").create_index(
                [("code", pymongo.ASCENDING), ("date", pymongo.DESCENDING)],
                unique=True
            )
        if "check_point" not in self.db.list_collection_names():
            self.get_table("check_point").create_index(
                [("code", pymongo.ASCENDING)],
                unique=True
            )

        if "check_point_time" not in self.db.list_collection_names():
            self.get_table("check_point_time").create_index(
                [("time", pymongo.DESCENDING)],
                unique=True
            )

        if "daily_check_point_time" not in self.db.list_collection_names():
            self.get_table("daily_check_point_time").create_index(
                [("date", pymongo.DESCENDING)],
                unique=True
            )

if __name__ == "__main__":
    """
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
    """
    db = MongoDbManager('localhost', 'hts')
    # list = db.dist("stock_info", "categoryC")
    # print(list)
    # sum = 0
    # for i in list:
    #     c = db.count("stock_info", {"categoryC": i})
    #     sum += c
    #     print("{0}: {1}".format(i, c))
    #
    # print(sum)
    start = datetime(2020, 11, 3, 0, 0, 0, 0)
    end = datetime(2020, 11, 3, 23, 59, 59, 999)

    list = db.dist("stock_real", "code", query={"time": {"$gte": start, "$lt": end}})
    print(len(list))
