from PyQt5.QtCore import QEventLoop
from util.logUtil import CommonLogger as log

class SyncRequestDecorator:
    """키움 API 비동기 함수 데코레이터
    """
    @staticmethod
    def kiwoom_sync_request(func):
        def func_wrapper(self, *args, **kwargs):
            if kwargs.get('nPrevNext', 0) == 0:
                log.instance().logger().debug('초기 요청 준비')
                self.params = {}
                self.result = {}
            # self.request_thread_worker.request_queue.append((func, args, kwargs))
            log.instance().logger().debug("요청 실행: %s %s %s" % (func.__name__, args, kwargs))
            func(self, *args, **kwargs)
            self.event = QEventLoop()
            self.event.exec_()
            return self.result  # 콜백 결과 반환
        return func_wrapper

    @staticmethod
    def kiwoom_sync_callback(func):
        def func_wrapper(self, *args, **kwargs):
            log.instance().logger().debug("요청 콜백: %s %s %s" % (func.__name__, args, kwargs))
            func(self, *args, **kwargs)  # 콜백 함수 호출
        return func_wrapper