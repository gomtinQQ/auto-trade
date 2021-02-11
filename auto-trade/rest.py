import sys

from tornado.web import Application
from tornado.ioloop import IOLoop
from PyQt5.QtWidgets import QApplication

from util.logUtil import CommonLogger as log
from restful.handler.accountHandler import AccountHandler
from restful.handler.stockHandler import StockHandler
from restful.handler.stockDailyHandler import StockDailyHandler
from restful.handler.realtimeHandler import RealTimeHandler
from restful.handler.realtimeRemoveHandler import RealTimeRemoveHandler
from restful.handler.stockCodeHandler import StockCodeHandler
from restful.handler.fileStoreHandlerHandler import FileStoreHandler
from kiwoom.kiwoom import Kiwoom
from db.mdb import MongoDbManager
import time

app = QApplication(sys.argv)
db = MongoDbManager('localhost', 'antwits')
hts = Kiwoom(db)

SLEEP_TIME = 0.1

def make_app():
    urls = [
        ("/accounts", AccountHandler, dict(SLEEP_TIME=SLEEP_TIME, hts=hts)),
        ("/stocks", StockHandler, dict(SLEEP_TIME=SLEEP_TIME, hts=hts)),
        ("/stocks-daily", StockDailyHandler, dict(SLEEP_TIME=SLEEP_TIME, hts=hts)),
        ("/real", RealTimeHandler, dict(SLEEP_TIME=SLEEP_TIME, hts=hts, db=db)),
        ("/remove", RealTimeRemoveHandler, dict(SLEEP_TIME=SLEEP_TIME, hts=hts, db=db)),
        ("/code", StockCodeHandler, dict(SLEEP_TIME=SLEEP_TIME, hts=hts, db=db)),
        ("/store", FileStoreHandler, dict(db=db))
    ]
    # Autoreload seems troublesome.
    return Application(urls, debug=True, autoreload=False)


if __name__ == "__main__":
    # login
    if hts.kiwoom_GetConnectState() != 0:
        log.instance().logger().debug('Connection failed')
        sys.exit()

    log.instance().logger().debug('로그인 시도')
    res = hts.kiwoom_CommConnect()
    if res.get('result') != 0:
        log.instance().logger().debug('Login failed')
        sys.exit()

    # To see list of your accounts...
    if True:
        accounts = hts.kiwoom_GetAccList()
        log.instance().logger().debug("Your accounts:")
        for acc in accounts:
            log.instance().logger().debug(acc)

    port = 5000
    tornado_app = make_app()
    tornado_app.listen(port)
    # tornado.autoreload.add_reload_hook(shutdown)
    log.instance().logger().debug('RESTful api server started at port {}'.format(port))

    # hts.clear_market_state("")
    # hts.clear_market_state("1000")
    # hts.remove_real()
    # hts.check_market_open()
    # hts.check_market_state("code001", "008350;000400", 0)
    # hts.check_market_state("code001", "008350;000400", "0")
    # hts.commKwRqData("352820;353200", 2, "종목정보 테스트", "10000")
    #try:
    #    IOLoop.instance().start()
    #except KeyboardInterrupt:
    #    shutdown()
    # Nothing to do for shutdown so... commenting out.

    # hts.store_daily_real_stock("000020", "20201203 09", "20201203 10")
    IOLoop.instance().start()

