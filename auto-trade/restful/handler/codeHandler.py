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
        log.instance().logger().debug("restore kospi list")

        hts = self.hts
        hts.deposit = None
        result = hts.load_code_list()

        log.instance().logger().debug("restored")
        self.write(json.dumps({'code': 'ok'}))