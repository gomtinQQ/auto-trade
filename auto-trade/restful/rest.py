import sys

from tornado.web import Application
from tornado.ioloop import IOLoop
from PyQt5.QtWidgets import QApplication

from util.logUtil import CommonLogger as log
from restful.handler.AccountHandler import AccountHandler
from kiwoom.kiwoom import Kiwoom


app = QApplication(sys.argv)
hts = Kiwoom()

SLEEP_TIME = 0.1

def make_app():
    urls = [
        ("/account", AccountHandler, dict(SLEEP_TIME=SLEEP_TIME, hts=hts)),
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

    #try:
    #    IOLoop.instance().start()
    #except KeyboardInterrupt:
    #    shutdown()
    # Nothing to do for shutdown so... commenting out.

    IOLoop.instance().start()