from flask import Flask, request, abort
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
import json
import hashlib
import uuid

app = Flask(__name__)
socketio = SocketIO(app)
mongoClient = MongoClient('mongodb://localhost:27017/')
db = mongoClient['pymessage']
user_col = db['user']

user_id_to_sid = {}
sid_to_user_id = {}


@app.route('/register', methods=['POST'])
def register_user():
    if not request.json:
        abort(400)
    if user_col.find_one({'user_id': request.json['user_id']}):
        return json.dumps({
            'msg': 'User already exists.'
        }), 409
    salt = uuid.uuid4().hex
    user = {
        'user_id': request.json['user_id'],
        'salt': salt,
        'password': hashlib.sha512((request.json['password'] + salt).encode('utf-8')).digest()
    }
    user_col.insert_one(user)
    return json.dumps({
            'msg': 'User created successfully.'
        }), 200


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
