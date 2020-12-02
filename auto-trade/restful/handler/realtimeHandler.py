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
        table_name = "stock"
        list_temp = self.db.dist(table_name, "code")
        size = 100
        page = 1
        count = len(list_temp)

        def isNotEmpty(x):
            return len(x) > 0

        # self.hts.get_daily_stock_open_status()
        # time.sleep(2)
        for i in range(0, count, size):
            code_list = list_temp[i:  i + size if size + i <= count else count]
            log.instance().logger().debug("SET REAL RES: {0} {1}".format(page, code_list))
            self.hts.set_real_stocks(code_list)
            code_list = list(filter(isNotEmpty, code_list))
            if page == 1:
                self.hts.set_check_market_state("{0:05}".format(page), ";".join(code_list), "0")
            else:
                self.hts.set_check_market_state("{0:05}".format(page), ";".join(code_list), "1")
                # print("")
            time.sleep(2)
            page += 1
        self.hts.multiEvents["STOCK"] = QEventLoop()
        self.hts.multiEvents["STOCK"].exec_()

