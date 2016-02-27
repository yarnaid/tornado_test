from datetime import datetime
import logging
import json

from tornado.ioloop import IOLoop
from tornado.tcpserver import TCPServer
from tornado import gen
from tornado.netutil import bind_sockets
from tornado.process import fork_processes
from tornado.websocket import WebSocketHandler
from tornado import web
from tornado.queues import PriorityQueue

import config
import helpers


logger = logging.getLogger()


class SocketHandler(WebSocketHandler):
    """
        Description
        -----------
        Socket for messages exchange
    """

    def __init__(self, *args, **kwargs):
        logger.debug('WebSocket started')
        super(SocketHandler, self).__init__(*args, **kwargs)

    def initialize(self, message_server):
        self.message_server = message_server

    def open(self):
        self.message_server.sockets.add(self)
        workers = filter(lambda c: c.name is not None, self.message_server._workers)
        connections = [{'name': c.name, 'id': c.id} for c in workers]
        self.write_message(json.dumps({'active': connections}))

    def on_close(self):
        self.message_server.sockets.remove(self)

    def check_origin(self, origin):
        return True


class Worker(object):
    """
        Description
        -----------
        Worker for stream proccessing
    """
    stream = None
    address = None
    is_authed = None
    name = None
    id = None
    _queue = None

    def __init__(self, stream, address, server=None):
        self.stream = stream
        self.address = address
        self.is_authed = False
        self.last_message = None
        self.server = server
        self.id = hash(datetime.now())
        self._queue = PriorityQueue()
        self._queue.join()
        logger.debug('Worker for {} is initiated'.format(address))

    def run(self):
        self.stream.set_close_callback(lambda: self.on_close(hard=True))
        self._read_line()

    def on_close(self, hard=False):
        self._queue.put((300, self.sockets_broadcast('closed', self.name)))
        self.is_authed = False
        self.name = None
        if self.stream and \
                self.stream.closed() and \
                self in self.server._workers and \
                hard:
            self.server._workers.remove(self)
        logger.debug("worker for {} is closed".format(self.address))

    def on_auth(self, message):
        self.is_authed = True
        self.name = message.value
        self._queue.put((1, self.sockets_broadcast('opened', self.name)))

    @gen.coroutine
    def sockets_broadcast(self, label, message):
        if self.server and self.is_authed:
            msg = {label: message, 'worker': self.name, 'id': self.id}
            msg = unicode(json.dumps(msg))
            for socket in self.server.sockets:
                socket.write_message(msg)

    @gen.coroutine
    def _read_line(self):
        self.stream.read_until(helpers.ENDING, self._handle_read)

    @gen.coroutine
    def _handle_read(self, data_):
        if not self.stream.closed():
            data = data_.rstrip()
            message = helpers.Message(data)
            logger.debug('[{}][{}][{}]'.format(self.address, unicode(message), data))
            if message.type == helpers.Message.MESSAGE and self.is_authed:
                self.last_message = message
                self._queue.put((100, self.sockets_broadcast('message', unicode(message))))
            if not self.is_authed:
                if message.type == helpers.Message.AUTH:
                    self.on_auth(message)
            else:
                if message.type == helpers.Message.END:
                    self.on_close()
            self._read_line()


class MessageServer(TCPServer):
    """
        Description
        -----------
        TCP connections server
    """
    sockets = set()

    def __init__(self, *args, **kwargs):
        logger.debug('Server is started')
        self._workers = set()
        super(MessageServer, self).__init__(*args, **kwargs)

    @gen.coroutine
    def handle_stream(self, stream, address):
        logger.debug('new connection {} {}'.format(address, stream))
        worker = Worker(stream, address, self)
        self._workers.add(worker)
        worker.run()


def main():
    config.parse_command_line()
    if config.options.debug:
        logging.basicConfig(level=logging.DEBUG)
    server = MessageServer()
    server.bind(config.options.port_tcp)
    server.start(config.options.workers)
    app = web.Application([
        (r'/', SocketHandler, {'message_server': server}),
        ],
        autoreload=False if config.options.debug else config.options.autoreload,
        debug=config.options.debug,
    )
    app.listen(config.options.port_socket)
    IOLoop.instance().start()
    IOLoop.instance().close()


if __name__ == '__main__':
    main()
