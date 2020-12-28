#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
# import sys
import os
import time
import boto3
import json
# import threading
# from threading import Event, Lock

from PyQt5.QAxContainer import QAxWidget
# from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
# from PyQt5.QtCore import QThread
# from PyQt5.QtCore import QEventLoop
# from PyQt5.QtWidgets import QApplication
#
# import numpy as np
# import pandas as pd

from util.logUtil import CommonLogger as log
from kiwoom.SyncRequestDecorator import SyncRequestDecorator
from kiwoom.code import KiwoomCode, RealType
from kiwoom.kiwoom_util import Kiwoom_tr_parse_util
from kiwoom.kiwoom_error import kiwoom_errors as errors


class Kiwoom(QAxWidget):
    def __init__(self, db):
        print("kiwoom start")
        super().__init__()

        self.SLEEP_TIME = 0.2
        self.LONG_SLEEP_TIME = 4

        self.db = db

        self.realType = RealType()

        # 키움 시그널 연결
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.OnEventConnect.connect(self.kiwoom_OnEventConnect)
        self.OnReceiveTrData.connect(self.kiwoom_OnReceiveTrData)
        self.OnReceiveRealData.connect(self.kiwoom_OnReceiveRealData)
        #self.OnReceiveRealCondition.connect(self.kiwoom_OnReceiveRealCondition)

        self.code = KiwoomCode()
        self.tr_util = Kiwoom_tr_parse_util()

        # self.OnReceiveConditionVer.connect(self.kiwoom_OnReceiveConditionVer)
        # self.OnReceiveTrCondition.connect(self.kiwoom_OnReceiveTrCondition)
        # self.OnReceiveRealCondition.connect(self.kiwoom_OnReceiveRealCondition)
        # self.OnReceiveChejanData.connect(self.kiwoom_OnReceiveChejanData)
        # self.OnReceiveMsg.connect(self.kiwoom_OnReceiveMsg)

        self.dict_callback = {}
        self.dict_callback_temp = None
        # 요청 결과
        self.event = None
        self.multiEvents = {}
        self.result = {}
        self.dict_call_param = {}

        # 장 상태
        self.market_state_screen = "1000"
        self.market_state_fid = "251"
        self.market_state_open = False
        self.market_real_table = "stock_real"

        # 실시간 장 정보
        self.real_stocks = {}

        # 5분 단위 체크 포인트 정보
        self.check_point = {"saving": False, "last": None, "term": 5}

        secret_key = os.environ.get("AWS_SECRET_KEY")
        access_key = os.environ.get("AWS_ACCESS_KEY")

        self.s3 = boto3.resource(
            's3',
            region_name='ap-northeast-2',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )

    # -------------------------------------
    # 로그인 관련함수
    # -------------------------------------
    @SyncRequestDecorator.kiwoom_sync_request
    def kiwoom_CommConnect(self, **kwargs):
        """로그인 요청 (키움증권 로그인창 띄워줌. 자동로그인 설정시 바로 로그인 진행)
        OnEventConnect() 콜백
        :param kwargs:
        :return: 1: 로그인 요청 성공, 0: 로그인 요청 실패
        """
        lRet = self.dynamicCall("CommConnect()")
        return lRet

    def kiwoom_GetConnectState(self, **kwargs):
        """로그인 상태 확인
        OnEventConnect 콜백
        :param kwargs:
        :return: 0: 연결안됨, 1: 연결됨
        """
        lRet = self.dynamicCall("GetConnectState()")
        return lRet

    def kiwoom_GetAccList(self):
        """
        Get account list
        :return: accout list, in python list form.
        """
        raw = self.dynamicCall("GetLoginInfo(\"ACCLIST\")")
        temp = self.dynamicCall("GetLoginInfo(\"USER_ID\")")
        print("USER ID {0}".format(temp))
        result = raw.split(";")
        if result[-1] == '':
            result.pop()
        return result

    def set_market_state(self, sCode):
        value = self.kiwoom_GetRealData(sCode, self.market_state_fid)
        if(value == '0'):
            # 장시작전
            self.market_state_open = False
        elif(value == '3'):
            # 장 시작
            self.market_state_open = True
        elif (value == '3'):
            # 장 종료 동시호가
            self.market_state_open = False
        elif (value == '3'):
            # 장 종료
            self.market_state_open = False
        return value

    @SyncRequestDecorator.kiwoom_sync_callback
    def kiwoom_OnEventConnect(self, nErrCode, **kwargs):
        """로그인 결과 수신
        로그인 성공시 [조건목록 요청]GetConditionLoad() 실행
        :param nErrCode: 0: 로그인 성공, 100: 사용자 정보교환 실패, 101: 서버접속 실패, 102: 버전처리 실패
        :param kwargs:
        :return:
        """
        if nErrCode == 0:
            log.instance().logger().debug("로그인 성공")
        elif nErrCode == 100:
            log.instance().logger().debug("사용자 정보교환 실패")
        elif nErrCode == 101:
            log.instance().logger().debug("서버접속 실패")
        elif nErrCode == 102:
            log.instance().logger().debug("버전처리 실패")

        self.result['result'] = nErrCode
        if self.event is not None:
            self.event.exit()

    def kiwoom_GetAccList(self):
        """
        Get account list
        :return: accout list, in python list form.
        """
        raw = self.dynamicCall("GetLoginInfo(\"ACCLIST\")")
        temp = self.dynamicCall("GetLoginInfo(\"USER_ID\")")
        print("USER ID {0}".format(temp))
        result = raw.split(";")
        if result[-1] == '':
            result.pop()
        return result

    @SyncRequestDecorator.kiwoom_sync_request
    def kiwoom_tr_account_balance(self, accountNo, screenNo, **kwargs):
        """예수금상세현황요청
        :param accountNo: 계좌번호
        :param kwargs:
        :return:
        """
        res = self.kiwoom_SetInputValue("계좌번호", accountNo)
        res = self.kiwoom_CommRqData("예수금상세현황요청", "opw00001", 0, screenNo)
        return res

    # -------------------------------------
    # 조회 관련함수
    # -------------------------------------
    def kiwoom_SetInputValue(self, sID, sValue):
        """
        :param sID:
        :param sValue:
        :return:
        """
        res = self.dynamicCall("SetInputValue(QString, QString)", sID, sValue)
        return res

    def set_input(self, data):
        for key, value in data.items():
            log.instance().logger().debug("K : {0} | V : {1}".format(key, value))
            self.kiwoom_SetInputValue(key, value)

    def kiwoom_CommRqData(self, sRQName, sTrCode, nPrevNext, sScreenNo):
        """
        :param sRQName:
        :param sTrCode:
        :param nPrevNext:
        :param sScreenNo:
        :return:
        """
        res = self.dynamicCall("CommRqData(QString, QString, int, QString)", sRQName, sTrCode, nPrevNext, sScreenNo)
        log.instance().logger().debug("CommRqData RES: {0}".format(res))
        if res < 0:
            log.instance().logger().debug("CommRqData RES: {0}".format(errors(res)))
            self.event.exit()
        return res

    def kiwoom_GetCommData(self, sTRCode, sRQName, nIndex, sItemName):
        """
        :param sTRCode:
        :param sRQName:
        :param nIndex:
        :param sItemName:
        :return:
        """
        res = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTRCode, sRQName, nIndex, sItemName)
        return res

    def set_real_stocks(self, codes):
        for c in codes:
            self.real_stocks[c] = {
                "time": None
            }

    def set_check_market_state(self, screenId, codes, addType=1):
        self.check_market_state(screenId, codes, addType)

    def check_market_open(self):
        fid = "215;20;214"
        res = self.dynamicCall("SetRealReg(QString, QString, QString, QString)", "1000", "", fid, "0")
        log.instance().logger().debug("SetRealReg RES: {0}".format(res))
        if res < 0:
            log.instance().logger().debug("SetRealReg RES: {0}".format(errors(res)))
            self.event.exit()

    def remove_real(self):
        res = self.dynamicCall("SetRealRemove(QString, QString)", "ALL", "ALL")
        log.instance().logger().debug("SetRealRemove RES: {0}".format(res))

    def clear_market_state(self, screen=""):
        res = self.dynamicCall("DisconnectRealData(QString)", screen)
        res = 1
        log.instance().logger().debug("DisconnectRealData RES: {0}".format(res))

    # @SyncRequestDecorator.kiwoom_sync_request
    def check_market_state(self, screenId, codes, addType="1"):
        # fid = "10;20;11;12;15;13;14;15;29;567;568;"
        fid = "10;20"
        res = self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screenId, codes, fid, addType)
        log.instance().logger().debug("SetRealReg RES: {0} {1} {2} {3} {4}".format(res, screenId, codes, fid, addType))
        if res < 0:
            log.instance().logger().debug("SetRealReg RES ERROR: {0}".format(errors(res)))
            # self.event.exit()
        else:
            log.instance().logger().debug("SetRealReg RES SUCCESS: {0}".format(errors(res)))
            # self.multiEvents[screenId] = QEventLoop()
            # self.multiEvents[screenId].exec_()
            # self.event.exit()
        return res

    def kiwoom_OnReceiveRealData(self, sCode, sRealType, sRealData):
        # log.instance().logger().debug("REAL DATA: {0}, {1}, {2}".format(sCode, sRealType, sRealData))
        if sRealType == "장시작시간":
            self.set_market_state(sCode)
        elif sRealType == "주식체결":
            # log.instance().logger().debug("주식 체결: {0}".format(self.get_real_stock_info(sCode, sRealType)))\
            self.get_real_stock_info(sCode, sRealType)
            # self.event.exit()

    def get_real_stock_info(self, sCode, sRealType):

        # 10;20;11;12;15;13;14;15;29;567;568;
        cmd = "GetCommRealData(QString, int)"
        # 출력 HHMMSS
        a = self.dynamicCall(cmd, sCode, self.realType.REALTYPE[sRealType]['체결시간'])

        # 출력 : +(-)2520
        b = self.dynamicCall(cmd, sCode, self.realType.REALTYPE[sRealType]['현재가'])
        b = abs(int(b))

        # 출력 : +(-)2520
        c = self.dynamicCall(cmd, sCode, self.realType.REALTYPE[sRealType]['전일대비'])
        c = abs(int(c))

        # 출력 : +(-)12.98
        d = self.dynamicCall(cmd, sCode, self.realType.REALTYPE[sRealType]['등락율'])
        d = float(d)

        # 출력 : +240124  매수일때, -2034 매도일 때
        #g = self.dynamicCall(cmd, sCode, self.realType.REALTYPE[sRealType]['거래량'])
        #g = abs(int(g))

        # 출력 : 240124
        h = self.dynamicCall(cmd, sCode, self.realType.REALTYPE[sRealType]['누적거래량'])
        h = abs(int(h))
        cFmt = "%Y%m%d %H%M%S"
        date = datetime.datetime.now().strftime("%Y%m%d")
        # "amount": g,
        result = {
            "time": datetime.datetime.strptime("{0} {1}".format(date, a), cFmt),
            "code": sCode,
            "price": b,
            "diffPrice": c,
            "rate": d,
            "accAmount": h
        }
        # 실시간 최신 가격 정보 저장
        check_point = {
            "time": "{0} {1}".format(date, a),
            "code": sCode,
            "price": b,
            "diffPrice": c,
            "rate": d,
            "accAmount": h
        }
        # 125717
        fmt = '%H%M%S'
        now = datetime.datetime.strptime(a, fmt)
        prev = self.real_stocks[sCode]["time"]
        # 시간대별 정보 저장
        self.find_n_update_check_point(sCode, {
            "time": datetime.datetime.strptime("{0} {1}".format(date, a), cFmt),
            "code": sCode,
            "price": b,
            "diffPrice": c,
            "rate": d,
            "accAmount": h
        })
        # 10초에 한번씩만 저장하도록 수정
        if prev is None:
            self.real_stocks[sCode]["time"] = now
            self.real_stocks[sCode]["price"] = b
            self.db.add(self.market_real_table, result)
            # self.find_n_update_check_point(sCode, result)
            self.real_stocks[sCode]["info"] = check_point
            return

        diff = now - prev

        if diff.seconds >= 10 and self.real_stocks[sCode]["price"] == b:
            self.real_stocks[sCode]["time"] = now
            # self.real_stocks[sCode]["info"] = check_point
            return
        elif diff.seconds >= 10 and self.real_stocks[sCode]["price"] != b:
            self.real_stocks[sCode]["prev"] = self.real_stocks[sCode]["time"]
            self.real_stocks[sCode]["time"] = now
            self.real_stocks[sCode]["price"] = b
            self.db.add(self.market_real_table, result)
            # self.find_n_update_check_point(sCode, result)
            self.store_daily_real_stock(sCode)
            self.real_stocks[sCode]["info"] = check_point
            self.save_check_point()
            return

    def find_n_update_check_point(self, code, data):
        prev = self.db.find("check_point", {"code": code})
        if len(prev) == 0:
            self.db.add("check_point", data)
        else:
            self.db.edit("check_point", {"code": code}, data)
        return

    def save_check_point(self):
        now = datetime.datetime.now()
        if now.minute % self.check_point["term"] == 0 and not self.check_point["saving"]:
            if self.check_point["last"] is None or self.check_point["last"] != now.minute:
                print("store check point START {0}".format(now))
                self.check_point["saving"] = True
                self.check_point["last"] = now.minute
                ticker_list = []

                for item in self.real_stocks.values():
                    if item["time"] is not None:
                        ticker_list.append(item["info"])

                last_date = now.strftime("%Y%m%d")
                check_point_time = now.strftime("%H%M")
                list_json = json.dumps(ticker_list)
                list_b = bytes(list_json, 'utf-8')
                s3_object = self.s3.Object('antwits',
                                           'stock/{0}/checkpoint/{1}.json'.format(last_date, check_point_time))
                s3_object.put(Body=list_b)
                print("store check point END {0}".format(datetime.datetime.now()))
                self.db.add("check_point_time", {"time": "{0} {1}".format(last_date, check_point_time)})
                self.check_point["saving"] = False
        return

    def set_market_state(self, sCode):
        value = self.kiwoom_GetRealData(sCode, self.market_state_fid)
        if value == '0':
            # 장시작전
            self.market_state_open = False
        elif value == '3':
            # 장 시작
            self.market_state_open = True
        elif value == '3':
            # 장 종료 동시호가
            self.market_state_open = False
        elif value == '3':
            # 장 종료
            self.market_state_open = False
        return value


    def kiwoom_GetRealData(self, sCode, fid):
        return self.dynamicCall("GetCommRealData(QString, int)", sCode, fid)

    @SyncRequestDecorator.kiwoom_sync_callback
    def kiwoom_OnReceiveTrData(self, screen_no, tr_name, tr_code, record_name, pre_next, data_length, error_code, message, sSPlmMsg, **kwargs):
        """TR 요청에 대한 결과 수신 데이터 얻어오기 위해 내부에서 GetCommData() 호출
          GetCommData(
          BSTR tr_code,   // TR 이름
          BSTR tr_name,   // 레코드이름
          long nIndex,      // TR반복부
          BSTR strItemName) // TR에서 얻어오려는 출력항목이름
        :param screen_no: 화면번호
        :param tr_name: 사용자 구분명
        :param tr_code: TR이름
        :param record_name: 레코드 이름
        :param pre_next: 연속조회 유무를 판단하는 값 0: 연속(추가조회)데이터 없음, 2:연속(추가조회) 데이터 있음
        :param data_length: 사용안함
        :param error_code: 사용안함
        :param message: 사용안함
        :param sSPlmMsg: 사용안함
        :param kwargs:
        :return:
        """
        log.instance().logger().debug("TR name : {0} | code : {1}".format(tr_name, tr_code))
        if tr_name == "예수금상세현황요청":
            self.deposit = int(self.kiwoom_GetCommData(tr_code, tr_name, 0, "주문가능금액"))
            log.instance().logger().debug("예수금상세현황요청: %s" % (self.deposit,))
            if "예수금상세현황요청" in self.dict_callback:
                self.dict_callback["예수금상세현황요청"](self.deposit)

        response = None

        if self.code.in_code(tr_name):
            code_info = self.code.get_code_info(tr_name)
            if 'output' in code_info.keys():
                response = self.get_single_response(tr_code, tr_name, pre_next, code_info)
            elif 'output_list' in code_info.keys():
                response = self.get_multi_response(tr_code, tr_name, pre_next, code_info)

        # 임시 코드
        if tr_code.lower() == 'OPT10081'.lower():
            pre_next = '0'

        if isinstance(response, (dict)):
            self.dict_callback[tr_name] = response
            self.dict_callback_temp = None
        elif isinstance(response, (list)) and len(response) == 0:
            if self.dict_callback_temp is None:
                self.dict_callback[tr_name] = []
            else:
                self.dict_callback[tr_name] = self.dict_callback_temp.copy()
                self.dict_callback_temp = None
            pre_next = '0'
        elif pre_next == '0':
            if self.dict_callback_temp is None:
                self.dict_callback[tr_name] = response
            else:
                prev = self.dict_callback_temp.copy()
                self.dict_callback_temp = None
                prev.extend(response)
                self.dict_callback[tr_name] = prev
        elif pre_next == '':
            log.instance().logger().debug("다음이 없음")
        else:
            if self.dict_callback_temp is None:
                self.dict_callback_temp = response
            else:
                self.dict_callback_temp.extend(response)

            pre_next = self.kiwoom_tr_recall(tr_name, tr_code, screen_no, pre_next)

            if pre_next == '0':
                if self.dict_callback_temp:
                    temp = self.dict_callback_temp.copy()
                    self.dict_callback_temp = None
                    self.dict_callback[tr_name] = temp
                else:
                    self.dict_callback[tr_name] = []

        if self.event and pre_next != '2':
            self.event.exit()

    def kiwoom_tr_recall(self, tr_name, tr_code, screen_no, pre_next):
        time.sleep(3.6)
        time.sleep(self.LONG_SLEEP_TIME)

        log.instance().logger().debug("연속조회")
        if tr_code.lower() == 'OPT10081'.lower():
            log.instance().logger().debug("OPT10081는 안 함")
            # self.kiwoom_tr_daily_stock_info(self.dict_callback_temp[0]["code"], self.dict_callback_temp[len(self.dict_callback_temp)-1]["date"], pre_next, '0')
        elif tr_code.lower() == 'OPT10086'.lower():
            param = self.dict_call_param[tr_code]
            if param:
                # {"종목코드": code, "조회일자": date, "수정주가구분": type, 'last_date': last_date}
                response = self.dict_callback_temp
                last_date = param['last_date']
                selected_list = list(filter(lambda x: (x['date'] < last_date), response))
                if len(selected_list) == 0:
                    self.kiwoom_tr_daily_stock_info_detail(param["종목코드"], param["조회일자"], param['last_date'], pre_next, param["수정주가구분"])
                else:
                    pre_next = '0'

        return pre_next

    def get_multi_response(self, tr_code, tr_name, pre_next, output_format):
        list = []
        count = self.dynamicCall("GetRepeatCnt(QString, QString)", tr_code, tr_name)
        code = None
        log.instance().logger().debug("LIST COUNT: {0}".format(count))
        for i in range(0, count):
            data = {}

            for key, value in output_format["output_list"].items():
                kr = value["kr"]
                type = value["type"]
                value = self.kiwoom_GetCommData(tr_code, tr_name, i, kr).strip()
                data[key] = self.tr_util.parse_response(value, type)
            if i == 0:
                if 'code' in data.keys():
                    code = data["code"]
            else:
                if code:
                    data["code"] = code
            list.append(data)

        log.instance().logger().debug("TR: {0}\tDATA: {1}".format(tr_name, list))
        return list

    def get_single_response(self, tr_code, tr_name, pre_next, output_format):
        data = {}
        for key, value in output_format["output"].items():
            kr = value["kr"]
            type = value["type"]
            value = self.kiwoom_GetCommData(tr_code, tr_name, 0, kr).strip()
            data[key] = self.tr_util.parse_response(value, type)

        log.instance().logger().debug("TR: {0}\tDATA: {1}".format(tr_name, data))
        # self.dict_callback[tr_name] = data
        return data

    @SyncRequestDecorator.kiwoom_sync_request
    def kiwoom_tr_stock_info(self, code,  **kwargs):
        """주식기본정보요청
        :param strCode:
        :param kwargs:
        :return:
        """
        key = "OPT10001"
        info = self.code.get_code_info(key)
        self.set_input({"종목코드": code})
        self.kiwoom_CommRqData(key, key, 0, info['screen_no'])
        return key

    def get_stock_info(self, code):
        tr_code = self.kiwoom_tr_stock_info(code)['res']
        keys = self.dict_callback.keys()
        count = 0
        while tr_code not in keys:
            count += 1
            time.sleep(self.SLEEP_TIME)
            if count > self.SLEEP_TIME * 100:
                break

        return self.dict_callback.pop(tr_code, None)

    @SyncRequestDecorator.kiwoom_sync_request
    def kiwoom_tr_daily_stock_info_detail(self, code, date, last_date, pre_next='0', type='0'):
        """
        type: 0:수량, 1:금액(백만원)
        """
        key = "OPT10086"
        info = self.code.get_code_info(key)
        param = {"종목코드": code, "조회일자": date, "수정주가구분": type, 'last_date': last_date}
        self.dict_call_param[key] = param
        self.set_input(param)
        self.kiwoom_CommRqData(key, key, pre_next, info['screen_no'])
        return key

    def get_daily_stock_info_detail(self, code, date, type='0'):
        last_date = self.db.max('stock_daily', {'code': code}, 'date')
        yesterday = datetime.datetime.now() - datetime.timedelta(days=2)
        if date == last_date or last_date == yesterday:
            return []

        if not last_date:
            #last_date = datetime.datetime.now() - datetime.timedelta(days=2 * 2)
            last_date = datetime.datetime.now() - datetime.timedelta(days=2 * 365)
            last_date = last_date.strftime("%Y%m%d")

        tr_code = self.kiwoom_tr_daily_stock_info_detail(code, date, last_date)['res']
        keys = self.dict_callback.keys()

        count = 0

        while tr_code not in keys:
            count += 1
            print("WAIT: {0} / {1} : {2}".format(keys, code, count))
            time.sleep(self.SLEEP_TIME)
            if count > self.SLEEP_TIME * 20:
                break;
        result = self.dict_callback.pop(tr_code, None)
        filtered_list = []
        if result:
            filtered_list = list(filter(lambda x: (x
                                                and x['individual_amount'] != 0
                                                and x['institute_amount'] != 0
                                                and x['foreigner_amount'] != 0), result))

            for data in filtered_list:
                data['code'] = code

        return filtered_list

    @SyncRequestDecorator.kiwoom_sync_request
    def kiwoom_tr_daily_stock_info(self, code, date, pre_next='0', type='0'):
        key = "OPT10081"
        info = self.code.get_code_info(key)

        self.set_input({"종목코드": code
                        , "기준일자": date
                        , "수정주가구분": type
                        })
        self.kiwoom_CommRqData(key, key, pre_next, info['screen_no'])
        return key

    def get_daily_stock_info(self, code, date, type='0'):
        tr_code = self.kiwoom_tr_daily_stock_info(code, date)['res']
        keys = self.dict_callback.keys()
        while tr_code not in keys:
            print("WAIT: {0} / {1}".format(keys, code) )
            time.sleep(self.SLEEP_TIME)
        # last_date = self.db.max('code', {'code': code}, 'date')
        return self.dict_callback.pop(tr_code, None)

    def save_daily_stock_info(self, code, stock_list):
        table_name = 'stock_daily'
        last_date = self.db.max(table_name, {'code': code}, 'date')
        filtered_list = []
        if last_date is None:
            filtered_list = stock_list
        else:
            for data in stock_list:
                if data['date'] == last_date:
                    break
                filtered_list.append(data)
        if filtered_list:
            self.db.add(table_name, filtered_list)

    def load_daily_stock_info_by_kospi(self, date=None):
        if date is None:
            date = datetime.datetime.now().strftime("%Y%m%d")
        kospi_list = self.db.find('code'
                                  , {'date': date
                                      , 'standard_price': {'$gte': 5000}
                                      , 'PER': {'$gte': 8, '$lte': 20}
                                     }
                                  )
        # kospi_list = self.db.find('code', {'date': date, 'PER': {'$gte': 8}, 'PER': {'$lte': 20}})

        stored_list = self.db.find('stock_daily_record', {'date': date})

        size = len(kospi_list)
        count = 0
        # 3 mins sleep
        # time.sleep(1 * 3 * 60)

        for k in kospi_list:
            # time.sleep(self.SLEEP_TIME*3)
            code = k['code']
            temp_list = list(filter(lambda x: (x['code'] == code), stored_list))
            count += 1
            if len(temp_list) > 0:
                print("ALREADY STORED: ", code)
                continue
            time.sleep(self.LONG_SLEEP_TIME)
            print("load code: count {0} / size {1} ".format(count, size))
            stock_list = self.get_daily_stock_info_detail(code, date)
            self.save_daily_stock_info(code, stock_list)
            self.db.add('stock_daily_record', {'date': date, 'code': code})
            print(stock_list)

    def get_kospi_list(self, today=None, market_type="0"):
        """
            KOSPI 정보만 불러옴
            나중에는 코스닥도 한번
        """
        table_name = 'stock'
        ret = self.dynamicCall("GetCodeListByMarket(QString)", [market_type])
        temp_kospi_code_list = ret.split(';')
        kospi_code_list = []
        kospi_list = []
        if today is None:
            today = datetime.datetime.now().strftime("%Y%m%d")

        for v in temp_kospi_code_list:
            if not v:
                continue
            if int(v[:2]) <= 12:
                kospi_code_list.append(v)

        print(temp_kospi_code_list)
        print(kospi_code_list)
        # return kospi_code_list
        pre = self.db.find(table_name, {'date': today})
        # pre = self.db.find('code', {'date': '20200529'})
        print(len(pre))
        pre_code_list = []
        # { "address": { "$regex": "^S" } }
        codes = []
        if pre is not None:
            for x in pre:
                if 'code' in x.keys():
                    pre_code_list.append(x['code'])

        for code in kospi_code_list:

            if code in pre_code_list:
                log.instance().logger().debug("IT WAS STORED: {0}".format(code))
                continue

            time.sleep(self.SLEEP_TIME)
            last_price = self.dynamicCall("GetMasterLastPrice(QString)", [code])
            if last_price == '':
                last_price = 0
            else:
                last_price = int(last_price)

            item = {
                "code": code
                , "date": today
                # , "name": self.dynamicCall("GetMasterCodeName(QString)", [code])
                # , "stock_count": int(self.dynamicCall("GetMasterListedStockCnt(QString)", [code]))
                # (정상, 투자주의, 투자경고, 투자위험, 투자주의환기종목)
                , "company_state": self.dynamicCall("GetMasterConstruction(QString)", [code])
                # , "listing_date": self.dynamicCall("GetMasterListedStockDate(QString)", [code])
                # , "last_price": last_price
                # (정상, 투자주의, 투자경고, 투자위험, 투자주의환기종목)
                , "stock_state": self.dynamicCall("GetMasterStockState(QString)", [code])
            }

            time.sleep(self.SLEEP_TIME*14)
            print("종목 정보: ", item)

            # if '투자주의' in item["stock_state"] or '투자경고' in item["company_state"] or '투자위험' in item["company_state"] or '투자주의환기종목' in item["company_state"]:
            #     continue

            tr_code = self.kiwoom_tr_stock_info(code)['res']
            keys = self.dict_callback.keys()

            count = 0

            while tr_code not in keys and count < 20:
                time.sleep(self.SLEEP_TIME)
                count += 1
                # print("count ", count)

            if count >= 20:
                break

            detail = self.dict_callback.pop(tr_code, None)

            for key, value in detail.items():
                item[key] = value

            if market_type == "0":
                item["market"] = "KS"
            elif market_type == "10":
                item["market"] = "KQ"

            print("종목 상세 정보: ", item)
            kospi_list.append(item)

            self.db.add(table_name, item)

        # self.db.add('code', kospi_list)

        stored_list = self.db.find(table_name, {'date': today})
        # pre = self.db.find('code', {'date': '20200529'})
        # { "address": { "$regex": "^S" } }

        return stored_list

    @SyncRequestDecorator.kiwoom_sync_request
    def commKwRqData(self, codes,  codeCount, requestName, screenNo, inquiry=0, typeFlag=0):
        """
        복수종목조회 메서드(관심종목조회 메서드라고도 함).
        이 메서드는 setInputValue() 메서드를 이용하여, 사전에 필요한 값을 지정하지 않는다.
        단지, 메서드의 매개변수에서 직접 종목코드를 지정하여 호출하며,
        데이터 수신은 receiveTrData() 이벤트에서 아래 명시한 항목들을 1회 수신하며,
        이후 receiveRealData() 이벤트를 통해 실시간 데이터를 얻을 수 있다.
        복수종목조회 TR 코드는 OPTKWFID 이며, 요청 성공시 아래 항목들의 정보를 얻을 수 있다.
        종목코드, 종목명, 현재가, 기준가, 전일대비, 전일대비기호, 등락율, 거래량, 거래대금,
        체결량, 체결강도, 전일거래량대비, 매도호가, 매수호가, 매도1~5차호가, 매수1~5차호가,
        상한가, 하한가, 시가, 고가, 저가, 종가, 체결시간, 예상체결가, 예상체결량, 자본금,
        액면가, 시가총액, 주식수, 호가시간, 일자, 우선매도잔량, 우선매수잔량,우선매도건수,
        우선매수건수, 총매도잔량, 총매수잔량, 총매도건수, 총매수건수, 패리티, 기어링, 손익분기,
        잔본지지, ELW행사가, 전환비율, ELW만기일, 미결제약정, 미결제전일대비, 이론가,
        내재변동성, 델타, 감마, 쎄타, 베가, 로
        :param codes: string - 한번에 100종목까지 조회가능하며 종목코드사이에 세미콜론(;)으로 구분.
        :param inquiry: int - api 문서는 bool 타입이지만, int로 처리(0: 조회, 1: 남은 데이터 이어서 조회)
        :param codeCount: int - codes에 지정한 종목의 갯수.
        :param requestName: string
        :param screenNo: string
        :param typeFlag: int - 주식과 선물옵션 구분(0: 주식, 3: 선물옵션), 주의: 매개변수의 위치를 맨 뒤로 이동함.
        :return: list - 중첩 리스트 [[종목코드, 종목명 ... 종목 정보], [종목코드, 종목명 ... 종목 정보]]
        """

        if not (isinstance(codes, str)
                and isinstance(inquiry, int)
                and isinstance(codeCount, int)
                and isinstance(requestName, str)
                and isinstance(screenNo, str)
                and isinstance(typeFlag, int)):
            raise ParameterTypeError()

        res = self.dynamicCall("CommKwRqData(QString, QBoolean, int, int, QString, QString)",
                                      codes, inquiry, codeCount, typeFlag, requestName, screenNo)
        log.instance().logger().debug("CommKwRqData RES: {0}".format(res))
        if res < 0:
            log.instance().logger().debug("CommKwRqData RES: {0}".format(errors(res)))
            self.event.exit()

    def add_all_market_state(self):
        print("")

    def store_daily_real_stock(self, code, dummy_start=None, dummy_end=None):
        # print("store {0}".format(code))
        last_date = datetime.datetime.now().strftime("%Y%m%d")
        start = datetime.datetime.strptime(last_date + " 08:30:00", "%Y%m%d %H:%M:%S")
        end = datetime.datetime.strptime(last_date + " 16:00:00", "%Y%m%d %H:%M:%S")
        real_list = self.db.find(self.market_real_table, {'code': code, 'time': {'$gte': start, '$lte': end}})
        p = dummy_start
        n = dummy_end
        if p is None or n is None:
            p = self.real_stocks[code]["prev"].strftime("%Y%m%d %H")
            n = self.real_stocks[code]["time"].strftime("%Y%m%d %H")

        # print("pre store {0} - {1} : {2}".format(code, p, n))

        if p != n:
            print("store {0} - {1}".format(code, p))
            for i in real_list:
                i["time"] = i["time"].strftime("%Y%m%d %H:%M:%S")
            list_json = json.dumps(real_list)
            list_b = bytes(list_json, 'utf-8')
            s3_object = self.s3.Object('antwits', 'stock/{0}/daily/{1}_{2}.json'.format(last_date, code, p.split()[1]))
            s3_object.put(Body=list_b)


class ParameterTypeError(Exception):
    """ 파라미터 타입이 일치하지 않을 경우 발생하는 예외 """

    def __init__(self, msg="파라미터 타입이 일치하지 않습니다."):
        self.msg = msg

    def __str__(self):
        return self.msg