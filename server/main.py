from flask import Flask, request
from flask_socketio import SocketIO, emit
import json


app = Flask(__name__)
socketio = SocketIO(app)

user_id_to_sid = {}
sid_to_user_id = {}


@socketio.on('send_username')
def on_connect(user_id):
    for user, sid in user_id_to_sid.items():
        emit('new_user', user_id, room=sid)
        emit('new_user', user, room=request.sid)
    user_id_to_sid[user_id] = request.sid
    sid_to_user_id[request.sid] = user_id


@socketio.on('leaving')
def on_leave(user_id):
    del sid_to_user_id[user_id_to_sid[user_id]]
    del user_id_to_sid[user_id]
    for user_id, sid in user_id_to_sid.items():
        emit('user_disconnected', user_id, room=sid)


@socketio.on('message')
def on_message(json_data):
    data = json.loads(json_data)
    if data['user_id'] in user_id_to_sid:
        emit('receive_message', json.dumps({
            'user_id': sid_to_user_id[request.sid],
            'msg': data['msg']
        }), room=user_id_to_sid[data['user_id']])


if __name__ == '__main__':
    socketio.run(app)
