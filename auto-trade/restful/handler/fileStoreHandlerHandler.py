from tornado.web import RequestHandler
import os
import json
import boto3

class FileStoreHandler(RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self):
        secret_key = os.environ.get("AWS_SECRET_KEY")
        access_key = os.environ.get("AWS_ACCESS_KEY")

        s3 = boto3.resource(
            's3',
            region_name='ap-northeast-2',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )

        last_date = self.db.max("code", {}, "date")

        codes = self.db.find("code", {"date": last_date})
        size = len(codes)
        index = 1
        for c in codes:
            list = self.db.find("stock_yf_daily", {"code": c["code"]})
            if len(list) > 0:
                print("TOTAL: {0} / {1}: {2}".format(index, size, c["code"]))

                list_json = json.dumps(list)
                list_b = bytes(list_json, 'utf-8')
                s3.Object('antwits', 'stock/{0}/{1}.json'.format(c["date"], c["code"])).delete()
                object = s3.Object('antwits', 'stock/{0}/{1}.json'.format(c["date"], c["code"]))

                object.put(Body=list_b)

            list = self.db.find("stock_yf_daily", {"code": c["code"], "date": {"$gte": "20160101"}})
            if len(list) > 0:
                print("TOTAL: {0} / {1}: {2} 5years".format(index, size, c["code"]))

                list_json = json.dumps(list)
                list_b = bytes(list_json, 'utf-8')
                s3.Object('antwits', 'stock/{0}/5/{1}.json'.format(c["date"], c["code"])).delete()
                object = s3.Object('antwits', 'stock/{0}/5/{1}.json'.format(c["date"], c["code"]))

                object.put(Body=list_b)

            index += 1

