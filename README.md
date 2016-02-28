# tornado_test
Test project for tornado framework

`web_app.py` -- web-server<br/>
`server.py` -- backend for TCP connections and websocket<br/>
`client.py` -- fake clients

## defaut options
port_tcp: 8889<br/>
port: 8888<br/>
port_socket: 9000<br/>
workers: 1<br/>
host: 127.0.0.1<br/>
debug: False<br/>
autoreload: True<br/>
clients_number: 40<br/>
message_number: 40<br/>
time_interval: 0.05<br/>

## Start
`pip install -r requirenments.txt`
`python web_app.py`<br/>
`python server.py`<br/>
open browser 127.0.0.1:8888<br/>
`python client.py`

## TODO
Add test
