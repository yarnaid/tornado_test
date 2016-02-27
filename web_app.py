import os

from tornado.web import Application
from tornado.web import RequestHandler
from tornado.web import StaticFileHandler
from tornado.ioloop import IOLoop

import config


PATH = os.path.dirname(__file__)
STATIC_PATH = os.path.join(PATH, 'static')
TEMPLATE_PATH = os.path.join(PATH, 'templates')


class MainHandler(RequestHandler):
    def get(self):
        basic_host = (self.request.host).replace(':' + str(config.options.port), '')
        params = {
            'ws_url': '{}:{}'.format(basic_host, config.options.port_socket),
        }
        self.render('index.html', **params)


def main():
    config.parse_command_line()
    app = Application(
            [
                (r'/', MainHandler),
            ],
            template_path=TEMPLATE_PATH,
            static_path=STATIC_PATH,
            debug=config.options.debug,
            autoreload=config.options.autoreload
        )
    app.listen(config.options.port)
    IOLoop.current().start()


if __name__ == '__main__':
    main()
