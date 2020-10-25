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