import time
from datetime import datetime
import logging
from random import randint

from tornado.ioloop import IOLoop
from tornado.tcpclient import TCPClient
from tornado import gen
from tornado.queues import PriorityQueue

import config
import helpers


logger = logging.getLogger()


class Client(object):
    name = None
    conn = None
    max_count = None
    count = None
    dt = None
    _event_queue = None

    def __init__(self, name=None, max_count=10, dt=0.5, client_set=None):
        global clients_set
        self.name = name or hash(datetime.now())
        self.max_count = max_count
        self.dt = dt
        self.authorized = False
        self.count = 0
        if client_set is None:
            self.client_set = set()
            self.client_set.add(self)
        else:
            self.client_set = client_set
        self._event_queue = PriorityQueue()
        self._event_queue.join()
        logger.debug('client start {}'.format(self.name))
        IOLoop.current().spawn_callback(self.init)
        IOLoop.current().spawn_callback(self.start_produce)

    @gen.coroutine
    def init(self):
        logger.debug('client init {}'.format(self.name))
        self.conn = yield TCPClient().connect(
            config.options.host,
            config.options.port_tcp
            )
        s = self.create_message(helpers.Message.AUTH)
        self.conn.write(s)

    @gen.coroutine
    def exit(self, force=False):
        logger.debug('client exit {}'.format(self.name))
        if self.conn and not self.conn.closed():
            s = self.create_message(helpers.Message.END)
            priority = 300 if not force else 0
            self._event_queue.put((priority, self.conn.write(s)))
            self._event_queue.put((priority, self.conn.close()))
            if self in self.client_set:
                self.client_set.remove(self)
        if not self.client_set:
            IOLoop.instance().stop()
        print len(self.client_set)

    @gen.coroutine
    def start_produce(self):
        logger.debug('client producing {}'.format(self.name))
        while True:
            yield gen.sleep(self.dt)
            if not self.conn.closed():
                value = self.count
                key = randint(1, 1000)
                s = self.create_message(key=key, value=value)
                yield self._event_queue.put((100, self.conn.write(s)))
            self.count += 1
            if self.count >= self.max_count:
                break

        yield self.exit()
        logger.debug('client stopped {}'.format(self.name))

    def create_message(self, type_=helpers.Message.MESSAGE, key=None, value=None):
        res = None
        if type_ == helpers.Message.AUTH:
            res = helpers.get_auth_str(self.name)
        elif type_ == helpers.Message.END:
            res = helpers.get_end_str()
        elif type_ == helpers.Message.MESSAGE:
            res = helpers.format_string(key, value)
        return bytes(res)


def main():
    config.parse_command_line()
    if config.options.debug:
        logging.basicConfig(level=logging.DEBUG)
    logger.debug('main start')
    clients_number = config.options.clients_number
    max_count = config.options.message_number
    client_set = set()
    for i in xrange(1, clients_number+1):
        name = randint(i, max_count)
        client_set.add(Client(
            name,
            max_count=max_count,
            dt=config.options.time_interval*10.,
            client_set=client_set
            ))
        time.sleep(config.options.time_interval)
    IOLoop.current().start()
    IOLoop.current().stop()


if __name__ == '__main__':
    logger.debug('starting')
    main()
