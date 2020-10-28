import time
import json

from tornado.web import RequestHandler
from util.logUtil import CommonLogger as log

class RealTimeRemoveHandler(RequestHandler):
    def initialize(self, SLEEP_TIME, hts, db):
        self.SLEEP_TIME = SLEEP_TIME
        self.hts = hts
        self.db = db

    def get(self):
        """
        remove real time stock info
        :return:
        """
        self.hts.remove_real()
        print("REMOVE ALL REAL")
