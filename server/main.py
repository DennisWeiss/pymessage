from flask import Flask, request, abort
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
import json
import hashlib
import uuid
import jwt
from apimessage import ApiMessage


app = Flask(__name__)
socketio = SocketIO(app)
mongoClient = MongoClient('mongodb://localhost:27017/')
db = mongoClient['pymessage']
user_col = db['user']

with open('conf.json', encoding='utf-8') as f:
    conf = json.loads(f.read())

user_id_to_sid = {}
sid_to_user_id = {}


@app.route('/register', methods=['POST'])
def register_user():
    if not request.json:
        abort(400)
    if user_col.find_one({'user_id': request.json['user_id']}):
        return json.dumps(ApiMessage('User already exists.').dict()), 409
    salt = uuid.uuid4().hex
    user = {
        'user_id': request.json['user_id'],
        'salt': salt,
        'password': hashlib.sha512((request.json['password'] + salt).encode('utf-8')).digest()
    }
    user_col.insert_one(user)
    return json.dumps(ApiMessage('User created successfully.').dict()), 200


@app.route('/login', methods=['POST'])
def login():
    if not request.json:
        abort(400)
    user = user_col.find_one({'user_id': request.json['user_id']})
    if not user:
        return json.dumps(ApiMessage('User does not exist.').dict()), 404
    print(hashlib.sha512((request.json['password'] + user['salt']).encode('utf-8')).digest())
    print(user['password'])
    if hashlib.sha512((request.json['password'] + user['salt']).encode('utf-8')).digest() == user['password']:
        return json.dumps({
            'user_id': request.json['user_id'],
            'auth_token': jwt.encode({'user_id': request.json['user_id']}, conf['JWT_SECRET'], algorithm='HS256').decode('utf-8')
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
