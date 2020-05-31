import time
import json

from tornado.web import RequestHandler

from util.logUtil import CommonLogger as log


class StockHandler(RequestHandler):
    def initialize(self, SLEEP_TIME, hts):
        self.SLEEP_TIME = SLEEP_TIME
        self.hts = hts

    def get(self):
        """
            restore kospi code
        """
        log.instance().logger().debug("code handler")

        code = self.get_argument('code', None)
        # query = self.get_argument('query', None)
        result = None
        # if query is not None:

        if code is None:
            result = self.reload_kospi()
        else:
            result = self.get_stock_info(code)

        self.write(json.dumps(result))

    def get_stock_info(self, code):
        hts = self.hts
        return hts.get_stock_infopop(code, None)

    def reload_kospi(self):
        hts = self.hts
        hts.deposit = None
        hts.get_kospi_list()
        hts.load_saily_stock_info_by_kospi()