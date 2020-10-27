import time
import json

from tornado.web import RequestHandler
from util.logUtil import CommonLogger as log


class AccountHandler(RequestHandler):
    def initialize(self, SLEEP_TIME, hts):
        self.SLEEP_TIME = SLEEP_TIME
        self.hts = hts

    def get(self):
        """
        Request data must contain
        accno : account number the transaction will happen
        """

        accno = self.get_argument('accno', None)

        # data = tornado.escape.json_decode(self.request.body)
        log.instance().logger().debug("BalanceHandler: incoming")
        # log.instance().logger().debug(data)

        hts = self.hts
        hts.deposit = None
        result = hts.kiwoom_tr_account_balance(accno, "1000")
        while not hts.deposit:
            time.sleep(self.SLEEP_TIME)
        cash = hts.deposit

        result = {}
        result["cash"] = cash

        log.instance().logger().debug("Response to client:")
        log.instance().logger().debug(str(result))
        self.write(json.dumps(result))