import socketio
import json


with open('conf.json', encoding='utf-8') as f:
    conf = json.loads(f.read())

sio = socketio.Client()
sio.connect(conf['SERVER_ADDRESS'])


def socket_io():
    return sio
