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

class Kiwoom(QAxWidget):
    def __init__(self, db):
        print("kiwoom start")
        super().__init__()

        self.db = db

        # 키움 시그널 연결
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.OnEventConnect.connect(self.kiwoom_OnEventConnect)
        self.OnReceiveTrData.connect(self.kiwoom_OnReceiveTrData)
        # self.OnReceiveRealData.connect(self.kiwoom_OnReceiveRealData)
        # self.OnReceiveConditionVer.connect(self.kiwoom_OnReceiveConditionVer)
        # self.OnReceiveTrCondition.connect(self.kiwoom_OnReceiveTrCondition)
        # self.OnReceiveRealCondition.connect(self.kiwoom_OnReceiveRealCondition)
        # self.OnReceiveChejanData.connect(self.kiwoom_OnReceiveChejanData)
        # self.OnReceiveMsg.connect(self.kiwoom_OnReceiveMsg)

        self.dict_callback = {}
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
    def kiwoom_OnReceiveTrData(self, sScrNo, sRQName, sTRCode, sRecordName, sPreNext, nDataLength, sErrorCode, sMessage, sSPlmMsg, **kwargs):
        """TR 요청에 대한 결과 수신
        데이터 얻어오기 위해 내부에서 GetCommData() 호출
          GetCommData(
          BSTR strTrCode,   // TR 이름
          BSTR strRecordName,   // 레코드이름
          long nIndex,      // TR반복부
          BSTR strItemName) // TR에서 얻어오려는 출력항목이름
        :param sScrNo: 화면번호
        :param sRQName: 사용자 구분명
        :param sTRCode: TR이름
        :param sRecordName: 레코드 이름
        :param sPreNext: 연속조회 유무를 판단하는 값 0: 연속(추가조회)데이터 없음, 2:연속(추가조회) 데이터 있음
        :param nDataLength: 사용안함
        :param sErrorCode: 사용안함
        :param sMessage: 사용안함
        :param sSPlmMsg: 사용안함
        :param kwargs:
        :return:
        """

        if sRQName == "예수금상세현황요청":
            self.deposit = int(self.kiwoom_GetCommData(sTRCode, sRQName, 0, "주문가능금액"))
            log.instance().logger().debug("예수금상세현황요청: %s" % (self.deposit,))
            if "예수금상세현황요청" in self.dict_callback:
                self.dict_callback["예수금상세현황요청"](self.deposit)

        if self.event is not None:
            self.event.exit()

    def load_code_list(self):
        ret = self.dynamicCall("GetCodeListByMarket(QString)", ["0"])
        kospi_code_list = ret.split(';')
        kospi_list = []
        today = datetime.datetime.now().strftime("%Y%m%d")

        for code in kospi_code_list:
            time.sleep(0.1)
            last_price = self.dynamicCall("GetMasterLastPrice(QString)", [code])
            if last_price == '':
                last_price = 0
            else:
                last_price = int(last_price)

            kospi_list.append({
                "code": code
                , "date": today
                , "name": self.dynamicCall("GetMasterCodeName(QString)", [code])
                , "stock_count": int(self.dynamicCall("GetMasterListedStockCnt(QString)", [code]))
                , "company_state": self.dynamicCall("GetMasterConstruction(QString)", [code])
                , "listing_date": self.dynamicCall("GetMasterListedStockDate(QString)", [code])
                , "last_price": last_price
                , "stock_state": self.dynamicCall("GetMasterStockState(QString)", [code])
            })

        self.db.add('code', kospi_list)
