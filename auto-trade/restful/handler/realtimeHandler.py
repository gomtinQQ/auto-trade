import time
import json

from tornado.web import RequestHandler
from util.logUtil import CommonLogger as log
from PyQt5.QtCore import QEventLoop

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
        # self.hts.get_daily_stock_open_status()
        # time.sleep(2)
        for i in range(1, count, size):
            result = self.db.page(table_name, page, size, {})
            if result is not None:
                codeList = []
                for c in result:
                    codeList.append(c["code"])
                log.instance().logger().debug("SET REAL RES: {0} {1}".format(page, codeList))
                if page == 1:
                    self.hts.set_check_market_state("STOCK{0:03}".format(page), ";".join(codeList), "0")
                else:
                    self.hts.set_check_market_state("STOCK{0:03}".format(page), ";".join(codeList), "1")
                    # print("")
                time.sleep(2)
            page += 1
        self.hts.multiEvents["STOCK"] = QEventLoop()
        self.hts.multiEvents["STOCK"].exec_()

