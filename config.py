from tornado.options import define, options, parse_command_line


define('port_tcp', default=8889, type=int)
define('port', default=8888, type=int)
define('port_socket', default=9000, type=int)
define('workers', default=1, type=int)
define('host', default='127.0.0.1')
define('debug', default=False, type=bool)
define('autoreload', default=True, type=bool)
define('clients_number', default=40, type=int)
define('message_number', default=40, type=int)
define('time_interval', default=0.05, type=float)
