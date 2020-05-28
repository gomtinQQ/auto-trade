import time
import json

from tornado.web import RequestHandler

from util.logUtil import CommonLogger as log


class CodeHandler(RequestHandler):
    def initialize(self, SLEEP_TIME, hts):
        self.SLEEP_TIME = SLEEP_TIME
        self.hts = hts

    def get(self):
        """
            restore kospi code
        """
        log.instance().logger().debug("code handler")

        code = self.get_argument('code', None)
        result = None
        if code is None:
            result = self.reload_code()
        else :
            result = self.get_stock_info(code)

        self.write(json.dumps(result))

    def get_stock_info(self, code):
        hts = self.hts

        tr_code = hts.kiwoom_tr_stock_info(code)['res']
        keys = hts.dict_callback.keys()
        while tr_code not in keys:
            time.sleep(self.SLEEP_TIME)

        return hts.dict_callback.pop(tr_code, None)

    def reload_code(self):
        hts = self.hts
        hts.deposit = None
        return hts.load_code_list()

