import pandas as pd
import json
import yfinance as yf
import datetime
from db.mdb import MongoDbManager

class Code_Crawler():
    def __init__(self, db):
        self.db = db
        self.table_name = "stock_category"
        self.yf_table_name = "stock_yf_daily_1030"
        self.today = datetime.datetime.now().strftime("%Y-%m-%d")
        print("CC: {0}".format(self.today))

    def clear(self):
        db.remove(self.table_name)

    def loadKospi(self):
        data = pd.read_csv("kospi.csv")
        data_json = json.loads(data.to_json(orient="records"))
        for i in data_json:
            # i["code"] = "{0:06d}".format(i["code"])
            i["code"] = i["code"].rjust(6, '0')
            i["market"] = "KS"
        print(data_json[0])
        db.add(self.table_name, data_json)
        for i in data_json:
            print(i)
            # self.loadYahooHistory(i["code"], i["market"])

    def loadKosdaq(self):
        data = pd.read_csv("kosdaq.csv")
        data_json = json.loads(data.to_json(orient="records"))
        for i in data_json:
            # i["code"] = "{0:06d}".format(int(i["code"]))
            i["code"] = i["code"].rjust(6, '0')
            i["market"] = "KQ"

        print(data_json[0])
        db.add(self.table_name, data_json)
        for i in data_json:
            print(i)
            # self.loadYahooHistory(i["code"], i["market"])

    def loadYahooHistory(self, code, market):
        last_date = self.db.max(self.yf_table_name, {'code': code}, 'date')
        ticker = yf.Ticker("{0}.{1}".format(code, market))

        if self.today == last_date:
            return

        hist = ticker.history(period="max") if last_date is None else ticker.history(start=last_date)
        data_json = json.loads(hist.to_json(orient="table"))
        data_lowercase = []
        for d in data_json["data"]:
            t = self.lower_dict(d)
            t["date"] = t["date"].split("T")[0]
            # data_lowercase.append(t)
            t["code"] = code
            # t["market"] = market
            data_lowercase.insert(0, t)

        # print(len(data_json["data"]))
        # print(len(data_lowercase))
        # print(data_lowercase[0])
        db.add(self.yf_table_name, data_lowercase)

    def lower_dict(self, d):
        new_dict = dict((k.lower(), v) for k, v in d.items())
        return new_dict


if __name__ == "__main__":
    db = MongoDbManager('localhost', 'antwits')
    c = Code_Crawler(db)
    c.clear()
    c.loadKospi()
    c.loadKosdaq()
    # c.loadYahooHistory("051910", "KS")
