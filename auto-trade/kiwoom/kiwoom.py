#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import sys
import os
import time
import threading
from threading import Event, Lock

from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QEventLoop
from PyQt5.QtWidgets import QApplication

import numpy as np
import pandas as pd

from util.logUtil import CommonLogger as log
from kiwoom.SyncRequestDecorator import SyncRequestDecorator
from kiwoom.code import KiwoomCode
from kiwoom.kiwoom_util import Kiwoom_tr_parse_util

class Kiwoom(QAxWidget):
    def __init__(self, db):
        print("kiwoom start")
        super().__init__()

        self.SLEEP_TIME = 0.2

        self.db = db

        # 키움 시그널 연결
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.OnEventConnect.connect(self.kiwoom_OnEventConnect)
        self.OnReceiveTrData.connect(self.kiwoom_OnReceiveTrData)

        self.code = KiwoomCode()
        self.tr_util = Kiwoom_tr_parse_util()

        # self.OnReceiveRealData.connect(self.kiwoom_OnReceiveRealData)
        # self.OnReceiveConditionVer.connect(self.kiwoom_OnReceiveConditionVer)
        # self.OnReceiveTrCondition.connect(self.kiwoom_OnReceiveTrCondition)
        # self.OnReceiveRealCondition.connect(self.kiwoom_OnReceiveRealCondition)
        # self.OnReceiveChejanData.connect(self.kiwoom_OnReceiveChejanData)
        # self.OnReceiveMsg.connect(self.kiwoom_OnReceiveMsg)

        self.dict_callback = {}
        self.dict_callback_temp = None
        # 요청 결과
        self.event = None
        self.result = {}

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
        result = raw.split(";")
        if result[-1] == '':
            result.pop()
        return result

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

        if self.event is not None:
            self.event.exit()

        # 임시 코드
        if tr_code.lower() == 'OPT10081'.lower():
            pre_next = 0

        if isinstance(response, (dict)):
            self.dict_callback[tr_name] = response
            self.dict_callback_temp = None
        elif isinstance(response, (list)) and len(response) == 0:
            self.dict_callback[tr_name] = self.dict_callback_temp.copy()
            self.dict_callback_temp = None
        elif pre_next == 0:
            if self.dict_callback_temp is None:
                self.dict_callback[tr_name] = response
            else:
                prev = self.dict_callback_temp.copy()
                self.dict_callback_temp = None
                self.dict_callback[tr_name] = prev.extend(response)
        else:
            if self.dict_callback_temp is None:
                self.dict_callback_temp = response
            else:
                self.dict_callback_temp.extend(response)
            self.kiwoom_tr_recall(tr_name, tr_code, screen_no, pre_next)

    def kiwoom_tr_recall(self, tr_name, tr_code, screen_no, pre_next):
        time.sleep(self.SLEEP_TIME)

        log.instance().logger().debug("연속조회")
        if tr_code.lower() == 'OPT10081'.lower():
            log.instance().logger().debug("OPT10081는 안 함")
            # self.kiwoom_tr_daily_stock_info(self.dict_callback_temp[0]["code"], self.dict_callback_temp[len(self.dict_callback_temp)-1]["date"], pre_next, '0')

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
                code = data["code"]
            else:
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
        while tr_code not in keys:
            time.sleep(self.SLEEP_TIME)

        return self.dict_callback.pop(tr_code, None)

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

    def save_daily_stock_info(self, code, list):
        table_name = 'stock_daily'
        last_date = self.db.max(table_name, {'code': code}, 'date')
        filtered_list = []
        if last_date is None:
            filtered_list = list
        else:
            for data in list:
                if data['date'] == last_date:
                    break
                filtered_list.append(data)
        if filtered_list:
            self.db.add(table_name, filtered_list)

    def load_saily_stock_info_by_kospi(self, date=None):
        if date is None:
            date = datetime.datetime.now().strftime("%Y%m%d")

        kospi_list = self.db.find('code', {'date': date, 'PER': {'$gte': 8}, 'PER': {'$lte': 20}})
        size = kospi_list.count(True)
        count = 0
        for k in kospi_list:
            time.sleep(self.SLEEP_TIME*3)
            code = k['code']
            count += 1
            print("load code: count {0} / size {1} ".format(count, size))

            list = self.get_daily_stock_info(code, date)
            self.save_daily_stock_info(code, list)
            print(list)

    def get_kospi_list(self, today=None):
        """
            KOSPI 정보만 불러옴
            나중에는 코스닥도 한번
        """
        ret = self.dynamicCall("GetCodeListByMarket(QString)", ["0"])
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
        pre = self.db.find('code', {'date': today})
        # pre = self.db.find('code', {'date': '20200529'})
        print(pre.count())
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

            time.sleep(self.SLEEP_TIME*3)
            print("종목 정보: ", item)

            if '투자주의' in item["stock_state"] or '투자경고' in item["company_state"] or '투자위험' in item["company_state"] or '투자주의환기종목' in item["company_state"]:
                continue

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

            print("종목 상세 정보: ", item)
            kospi_list.append(item)
            self.db.add('code', item)

        # self.db.add('code', kospi_list)

        stored_list = self.db.find('code', {'date': today})
        # pre = self.db.find('code', {'date': '20200529'})
        # { "address": { "$regex": "^S" } }
        result = []
        if stored_list is not None:
            for x in stored_list:
                if 'code' in x.keys():
                    x.pop('_id')
                    result.append(x)

        return result
