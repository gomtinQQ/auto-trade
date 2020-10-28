from PyQt5.QtCore import QEventLoop
from util.logUtil import CommonLogger as log
import inspect


class SyncRequestDecorator:
    """키움 API 비동기 함수 데코레이터
       """

    @staticmethod
    def kiwoom_sync_multi_request(func):
        def func_wrapper(self, *args, **kwargs):
            # self.request_thread_worker.request_queue.append((func, args, kwargs))
            arg_names = inspect.getfullargspec(func).args
            if 'pre_next' in arg_names:
                index = arg_names.index('pre_next') - 1
            else:
                index = -1

            log.instance().logger().debug("요청 실행: %s %s %s" % (func.__name__, args, kwargs))
            res = func(self, *args, **kwargs)
            if index < 0 or len(args) <= index or args[index] != '2':
                log.instance().logger().debug("EVENT INIT")
                self.event = QEventLoop()
                self.params = {}
                self.result = {}

            self.event.exec_()
            self.result['res'] = res
            return self.result  # 콜백 결과 반환

        return func_wrapper

    """키움 API 비동기 함수 데코레이터
    """
    @staticmethod
    def kiwoom_sync_request(func):
        def func_wrapper(self, *args, **kwargs):
            # self.request_thread_worker.request_queue.append((func, args, kwargs))
            arg_names = inspect.getfullargspec(func).args
            if 'pre_next' in arg_names:
                index = arg_names.index('pre_next') - 1
            else:
                index = -1

            log.instance().logger().debug("요청 실행: %s %s %s" % (func.__name__, args, kwargs))
            res = func(self, *args, **kwargs)
            if index < 0 or len(args) <= index or args[index] != '2':
                log.instance().logger().debug("EVENT INIT")
                self.event = QEventLoop()
                self.params = {}
                self.result = {}

            self.event.exec_()
            self.result['res'] = res
            return self.result  # 콜백 결과 반환
        return func_wrapper

    @staticmethod
    def kiwoom_sync_callback(func):
        def func_wrapper(self, *args, **kwargs):
            log.instance().logger().debug("요청 콜백: %s %s %s" % (func.__name__, args, kwargs))
            func(self, *args, **kwargs)  # 콜백 함수 호출
        return func_wrapper