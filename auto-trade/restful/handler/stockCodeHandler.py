import time
import json
import yfinance as yf
from tornado.web import RequestHandler
from datetime import datetime
from util.logUtil import CommonLogger as log


class StockCodeHandler(RequestHandler):
    def initialize(self, SLEEP_TIME, hts, db):
        self.SLEEP_TIME = SLEEP_TIME
        self.hts = hts
        self.db = db
        self.yf_table_name = "stock_yf_daily"

    def get(self):
        """
            restore kospi code
        """
        log.instance().logger().debug("code handler")

        # query = self.get_argument('query', None)
        # if query is not None:
        """
            [시장구분값]
            0 : 장내
            10 : 코스닥
            3 : ELW
            8 : ETF
            50 : KONEX
            4 :  뮤추얼펀드
            5 : 신주인수권
            6 : 리츠
            9 : 하이얼펀드
            30 : K-OTC
        """
        # KOSPI
        ks = self.reload_kospi("0")
        self.today = datetime.now().strftime("%Y%m%d")

        for i in ks:
            print(i)
            self.loadYahooHistory(i["code"], i["market"])

        # KOSDAQ
        kq = self.reload_kospi("10")

        for i in kq:
            print(i)
            self.loadYahooHistory(i["code"], i["market"])

        return {
            "ks": ks,
            "kq": kq
        }

    def reload_kospi(self, code):
        hts = self.hts
        hts.deposit = None
        return hts.get_kospi_list(market_type=code)
        # hts.load_daily_stock_info_by_kospi()

    def loadYahooHistory(self, code, market):
        last_date = self.db.max(self.yf_table_name, {'code': code}, 'date')
        ticker = yf.Ticker("{0}.{1}".format(code, market))

        if self.today == last_date:
            return

        if last_date is None:
            f_date = None
        else:
            f_date = "{0}-{1}-{2}".format(last_date[0:4], last_date[4:6], last_date[6:8])
        print("{0}-{1}".format(code, market))
        hist = ticker.history(period="max") if f_date is None else ticker.history(start=f_date)
        data_json = json.loads(hist.to_json(orient="table"))
        data_lowercase = []
        for d in data_json["data"]:
            if f_date != d["Date"].split("T")[0]:
                t = self.lower_dict(d)
                t["date"] = t["date"].split("T")[0].replace("-", "")
                # data_lowercase.append(t)
                t["code"] = code
                # t["market"] = market
                data_lowercase.insert(0, t)

        # print(len(data_json["data"]))
        # print(len(data_lowercase))
        # print(data_lowercase[0])
        if len(data_lowercase) > 0:
            self.db.add(self.yf_table_name, data_lowercase)

    def lower_dict(self, d):
        new_dict = dict((k.lower(), v) for k, v in d.items())
        return new_dict