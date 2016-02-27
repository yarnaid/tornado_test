import logging

AUTH_CODE = 'Auth'
STOP_CODE = 'End'
DELIMITER = ':: '
ENDING = '\r\n'
logger = logging.getLogger()


class Message(object):
    """
        Description
        -----------
        Message class for any string
    """

    AUTH, MESSAGE, END = range(3)
    key = None
    value = None
    type = None

    def __init__(self, s):
        self._string = s
        if s is not None:
            self.parse_str()

    def parse_str(self):
        res = check_auth_str(self._string)
        if res is not None:
            self.type = self.AUTH
            self.key = AUTH_CODE
            self.value = res
        elif check_stop(self._string):
            self.type = self.END
        else:
            try:
                self.key, self.value = parse_str(self._string)
                self.type = self.MESSAGE
            except ValueError:
                logger.error('VALUE ERROR FOR MESSAGE!', exc_info=1)
                self.type = None
                self.key = None
                self.value = None

    def __unicode__(self):
        return u' | '.join(map(unicode, [self.key, self.value]))

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return '<Message[{}]: {}>'.format(self.type, self.__str__)


def format_string(*args):
    if len(args) == 2 or len(args) == 1:
        return DELIMITER.join(map(unicode, args)) + ENDING
    else:
        raise ValueError('Wrong arguments number!')


def get_auth_str(name):
    return format_string(AUTH_CODE, name)


def get_end_str():
    return format_string(STOP_CODE)


def get_stop_str():
    return ''.join([STOP_CODE, ENDING])


def parse_str(s):
    if not isinstance(s, (str, unicode, bytearray, bytes)):
        raise ValueError('Wrong input type')

    values = None
    if s.count(DELIMITER) == 1:
        values = map(unicode, s.split(DELIMITER))
    elif s.count(DELIMITER) > 1:
        raise ValueError('Too many delimeters')
    elif s != STOP_CODE:
        raise ValueError('Wrong formatted string')

    return values


def check_auth_str(s):
    res = None
    values = parse_str(s)
    if values and values[0] == AUTH_CODE:
        res = values[1]
    return res


def check_stop(s):
    return STOP_CODE == s.rstrip()
