from util.logUtil import CommonLogger as log


class Kiwoom_tr_parse_util():
    def __init__(self):
        log.instance().logger().debug("Kiwoom_tr_parse_util init")

    def parse_response(self, value, type):
        value = value.replace('--', '-')
        if type == 'ui':
            if not value:
                value = '0'
            value = abs(int(value))
        elif type == 'i':
            if not value:
                value = '-1'
            value = int(value)
        elif type == 'f':
            if not value:
                value = '-1'
            value = float(value)
        elif type == 's':
            value = value
        # log.instance().logger().debug("TR: {0}\tDATA: {1}".format(value, type))
        return value

