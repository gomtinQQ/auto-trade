import time
import json

from tornado.web import RequestHandler
from util.logUtil import CommonLogger as log

class RealTimeHandler(RequestHandler):
    def initialize(self, SLEEP_TIME, hts, db):
        self.SLEEP_TIME = SLEEP_TIME
        self.hts = hts
        self.db = db

    def get(self):
        """
        get real time stock info
        :return:
        """
        table_name = "stock_info"
        count = self.db.count(table_name, {})
        size = 100
        page = 1
        for i in range(1, count, size):
            result = self.db.page(table_name, page, size, {})
            page += 1
            if result is not None:
                print(len(result))

