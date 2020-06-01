import datetime
import time
import json

from tornado.web import RequestHandler

from util.logUtil import CommonLogger as log


class StockDailyHandler(RequestHandler):
    def initialize(self, SLEEP_TIME, hts):
        self.SLEEP_TIME = SLEEP_TIME
        self.hts = hts

    def get(self):
        """
            restore kospi code
        """
        log.instance().logger().debug("stock daily handler")

        code = self.get_argument('code', None)
        today = self.get_argument('today', None)
        if today is None:
            today = datetime.datetime.now().strftime("%Y%m%d")

        result = None
        if code is not None:
            result = self.hts.get_daily_stock_info_detail(code, today)
            # self.hts.save_daily_stock_info(code, result)
        self.write(json.dumps(result))