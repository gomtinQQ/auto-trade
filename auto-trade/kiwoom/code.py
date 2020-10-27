class KiwoomCode():
    def __init__(self):
        self.code_info = {
            "OPT10001": {
                "name": "주식기본정보요청"
                , "screen_no": "10001"
                , "output": {
                    "code": {"kr": "종목코드", "type": "s"}
                    , "name": {"kr": "종목명", "type": "s"}
                    , "settlement_month": {"kr": "결산월", "type": "s"}
                    , "face_value": {"kr": "액면가", "type": "f"}
                    , "capital": {"kr": "자본금", "type": "i"}
                    , "stocks": {"kr": "상장주식", "type": "i"}
                    , "credit_ratio": {"kr": "신용비율", "type": "uf"}
                    , "high_year": {"kr": "연중최고", "type": "ui"}
                    , "low_year": {"kr": "연중최저", "type": "ui"}
                    , "total_market_value": {"kr": "시가총액", "type": "i"}
                    # , "": {"kr": "시가총액비중", "type": ""}
                    # , "": {"kr": "외인소진률", "type": ""}
                    # , "": {"kr": "대용가", "type": ""}
                    # 1주당 순이익 비율 Price Earnings Ratio (주가 / 주당순이익)
                    , "PER": {"kr": "PER", "type": "f"}
                    # 주당 순이익
                    , "EPS": {"kr": "EPS", "type": "i"}

                    , "ROE": {"kr": "ROE", "type": "f"}
                    # 1주당 순자산 비율 Price Book value Ratio
                    , "PBR": {"kr": "PBR", "type": "f"}
                    , "EV": {"kr": "EV", "type": "f"}
                    , "BSP": {"kr": "BPS", "type": "i"}
                    , "sales": {"kr": "매출액", "type": "i"}
                    , "business_profits": {"kr": "영업이익", "type": "i"}
                    , "net_profit": {"kr": "당기순이익", "type": "i"}
                    , "high_250": {"kr": "250최고", "type": "ui"}
                    , "low_250": {"kr": "250최저", "type": "ui"}
                    , "market_price": {"kr": "시가", "type": "ui"}
                    , "high": {"kr": "고가", "type": "ui"}
                    , "low": {"kr": "저가", "type": "ui"}
                    , "max_price": {"kr": "상한가", "type": "ui"}
                    , "min_price": {"kr": "하한가", "type": "ui"}
                    , "standard_price": {"kr": "기준가", "type": "i"}
                    , "estimated_price": {"kr": "예상체결가", "type": "ui"}
                    , "date_high_250": {"kr": "250최고가일", "type": "s"}
                    , "ratio_high_250": {"kr": "250최고가대비율", "type": "f"}
                    , "date_low_250": {"kr": "250최저가일", "type": "s"}
                    , "ratio_low_250": {"kr": "250최저가대비율", "type": "f"}
                    , "present_price": {"kr": "현재가", "type": "ui"}
                    # , "": {"kr": "대비기호", "type": ""}
                    , "net_change": {"kr": "전일대비", "type": "i"}
                    , "fluctuation_rate": {"kr": "등락율", "type": "f"}
                    , "volume": {"kr": "거래량", "type": "i"}
                    , "volume_change": {"kr": "거래대비", "type": "f"}
                    # , "": {"kr": "액면가단위", "type": ""}
                    , "outstanding_stock": {"kr": "유통주식", "type": "i"}
                    , "distribution_ratio": {"kr": "유통비율", "type": "f"}
                }
            }
            , "OPT10081": {
                "name": "주식일봉차트조회요청"
                , "screen_no": "20001"
                , "output_list": {
                    "code": {"kr": "종목코드", "type": "s"}
                    , "date": {"kr": "일자", "type": "s"}
                    , "present_price": {"kr": "현재가", "type": "f"}
                    , "volume": {"kr": "거래량", "type": "i"}
                    , "market_price": {"kr": "시가", "type": "ui"}
                    , "high": {"kr": "고가", "type": "ui"}
                    , "low": {"kr": "저가", "type": "ui"}
                }
            }
            , "OPT10086": {
                "name": "일별주가요청"
                , "screen_no": "20002"
                , "output_list": {
                    "date": {"kr": "날짜", "type": "s"}
                    , "market_price": {"kr": "시가", "type": "ui"}
                    , "high": {"kr": "고가", "type": "ui"}
                    , "low": {"kr": "저가", "type": "ui"}
                    , "close_price": {"kr": "종가", "type": "ui"}
                    , "net_change": {"kr": "전일비", "type": "i"}
                    , "fluctuation_rate": {"kr": "등락율", "type": "f"}
                    , "volume": {"kr": "거래량", "type": "i"}
                    , "individual_amount": {"kr": "개인", "type": "i"}
                    , "institute_amount": {"kr": "기관", "type": "i"}
                    , "foreigner_amount": {"kr": "외인수량", "type": "i"}
                    , "program_amount": {"kr": "프로그램", "type": "i"}
                    , "foreigner_volume": {"kr": "외인보유", "type": "f"}
                    , "foreigner_ratio": {"kr": "외인비중", "type": "f"}
                    , "foreigner_net_purchase": {"kr": "외인순매수", "type": "i"}
                    , "institute_net_purchase": {"kr": "기관순매수", "type": "i"}
                    , "individual_net_purchase": {"kr": "개인순매수", "type": "i"}
                }
            }
            , "": {

            }


        }

    def in_code(self, code):
        return code in self.code_info

    def get_code_info(self, code):
        return self.code_info[code]


class RealType(object):
    SENDTYPE = {
        '거래구분': {
            '지정가': '00',
            '시장가': '03',
            '조건부지정가': '05',
            '최유리지정가': '06',
            '최우선지정가': '07',
            '지정가IOC': '10',
            '시장가IOC': '13',
            '최유리IOC': '16',
            '지정가FOK': '20',
            '시장가FOK': '23',
            '최유리FOK': '26',
            '장전시간외종가': '61',
            '시간외단일가매매': '62',
            '장후시간외종가': '81'
        }
    }

    REALTYPE = {

        '주식체결': {
            '체결시간': 20,
            '현재가': 10,  # 체결가
            '전일대비': 11,
            '등락율': 12,
            '(최우선)매도호가': 27,
            '(최우선)매수호가': 28,
            '거래량': 15,
            '누적거래량': 13,
            '누적거래대금': 14,
            '시가': 16,
            '고가': 17,
            '저가': 18,
            '전일대비기호': 25,
            '전일거래량대비': 26,
            '거래대금증감': 29,
            '전일거래량대비': 30,
            '거래회전율': 31,
            '거래비용': 32,
            '체결강도': 228,
            '시가총액(억)': 311,
            '장구분': 290,
            'KO접근도': 691,
            '상한가발생시간': 567,
            '하한가발생시간': 568
        },

        '장시작시간': {
            '장운영구분': 215,
            '시간': 20,  # (HHMMSS)
            '장시작예상잔여시간': 214
        },

        '주문체결': {
            '계좌번호': 9201,
            '주문번호': 9203,
            '관리자사번': 9205,
            '종목코드': 9001,
            '주문업무분류': 912,  # (jj:주식주문)
            '주문상태': 913,
            # (접수, 확인, 체결) (10:원주문, 11:정정주문, 12:취소주문, 20:주문확인, 21:정정확인, 22:취소확인, 90,92:주문거부) #https://bbn.kiwoom.com/bbn.openAPIQnaBbsDetail.do
            '종목명': 302,
            '주문수량': 900,
            '주문가격': 901,
            '미체결수량': 902,
            '체결누계금액': 903,
            '원주문번호': 904,
            '주문구분': 905,  # (+매수, -매도, -매도정정, +매수정정, 매수취소, 매도취소)
            '매매구분': 906,  # (보통, 시장가등)
            '매도수구분': 907,  # 매도(매도정정, 매도취도 포함)인 경우 1, 매수(매수정정, 매수취소 포함)인 경우 2
            '주문/체결시간': 908,  # (HHMMSS)
            '체결번호': 909,
            '체결가': 910,
            '체결량': 911,
            '현재가': 10,
            '(최우선)매도호가': 27,
            '(최우선)매수호가': 28,
            '단위체결가': 914,
            '단위체결량': 915,
            '당일매매수수료': 938,
            '당일매매세금': 939,
            '거부사유': 919,
            '화면번호': 920,
            '터미널번호': 921,
            '신용구분(실시간 체결용)': 922,
            '대출일(실시간 체결용)': 923,
        },

        '매도수구분': {
            '1': '매도',
            '2': '매수'
        },

        '잔고': {
            '계좌번호': 9201,
            '종목코드': 9001,
            '종목명': 302,
            '현재가': 10,
            '보유수량': 930,
            '매입단가': 931,
            '총매입가': 932,
            '주문가능수량': 933,
            '당일순매수량': 945,
            '매도매수구분': 946,
            '당일총매도손익': 950,
            '예수금': 951,
            '(최우선)매도호가': 27,
            '(최우선)매수호가': 28,
            '기준가': 307,
            '손익율': 8019
        },
    }