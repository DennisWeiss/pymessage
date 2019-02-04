from flask import Flask, request, abort

from flask_socketio import SocketIO, emit
from pymongo import MongoClient
import json
import hashlib
import uuid
import jwt
from apimessage import ApiMessage
import re
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app)
mongoClient = MongoClient('mongodb://localhost:27017/')
db = mongoClient['pymessage']
user_col = db['user']

online_check_interval = 10

with open('conf.json', encoding='utf-8') as f:
    conf = json.loads(f.read())

user_id_to_sid = {}
sid_to_user_id = {}
sid_to_last_online_msg = {}


def disconnect_user(disconnected_user):
    for user_id, sid in user_id_to_sid.items():
        socketio.emit('user_disconnected', disconnected_user, room=sid)


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
    if hashlib.sha512((request.json['password'] + user['salt']).encode('utf-8')).digest() == user['password']:
        return json.dumps({
            'user_id': request.json['user_id'],
            'auth_token': jwt.encode(
                {'user_id': request.json['user_id']}, conf['JWT_SECRET'], algorithm='HS256'
            ).decode('utf-8')
        }), 200
    return json.dumps({
        'msg': 'Wrong password'
    }), 401


@app.route('/user', methods=['GET'])
def get_user():
    user = user_col.find_one({'user_id': request.args.get('id')})
    if not user:
        abort(404)
    return json.dumps({
        'user_id': user['user_id']
    }), 200


@app.route('/search-user', methods=['GET'])
def search_user():
    search_string = request.args.get('searchstring')
    users = list(user_col.find({'user_id': re.compile(search_string)}))
    return json.dumps(list(map(lambda user: user['user_id'], users))), 200


@app.route('/online', methods=['GET'])
def is_online():
    user_id = request.args.get('user')
    user = user_col.find({'user_id': user_id})
    if not user:
        abort(404)
    return json.dumps({
        'user_id': user_id,
        'online': user_id in user_id_to_sid
    })


@socketio.on('joining')
def on_join(json_data):
    data = json.loads(json_data)
    user_id = data['user_id']
    decoded_token = jwt.decode(data['auth_token'], conf['JWT_SECRET'], algorithms=['HS256'])
    if decoded_token is not None and decoded_token['user_id'] == user_id:
        for user, sid in user_id_to_sid.items():
            emit('new_user', user_id, room=sid)
            emit('new_user', user, room=request.sid)
        user_id_to_sid[user_id] = request.sid
        sid_to_user_id[request.sid] = user_id
        sid_to_last_online_msg[request.sid] = time.time()


@socketio.on('leaving')
def on_leave(json_data):
    data = json.loads(json_data)
    user_id = data['user_id']
    decoded_token = jwt.decode(data['auth_token'], conf['JWT_SECRET'], algorithms=['HS256'])
    if decoded_token is not None and decoded_token['user_id'] == user_id:
        disconnect_user(user_id)


@socketio.on('message')
def on_message(json_data):
    data = json.loads(json_data)
    user_id = data['user_id']
    decoded_token = jwt.decode(data['auth_token'], conf['JWT_SECRET'], algorithms=['HS256'])
    if decoded_token is not None and decoded_token['user_id'] == sid_to_user_id[request.sid]\
            and data['user_id'] in user_id_to_sid:
        emit('receive_message', json.dumps({
            'user_id': sid_to_user_id[request.sid],
            'msg': data['msg']
        }), room=user_id_to_sid[user_id])


@socketio.on('online')
def on_online_msg(data):
    print(sid_to_user_id[request.sid] + ' is online')
    if request.sid in sid_to_last_online_msg:
        sid_to_last_online_msg[request.sid] = time.time()


def check_if_users_are_still_online():
    threading.Timer(online_check_interval, check_if_users_are_still_online).start()
    print(sid_to_last_online_msg)
    users_to_remove = []
    for sid, last_online_msg in sid_to_last_online_msg.items():
        if time.time() - last_online_msg > 10:
            print(sid_to_user_id[sid] + ' is no longer online')
            disconnect_user(sid_to_user_id[sid])
            del user_id_to_sid[sid_to_user_id[sid]]
            del sid_to_user_id[sid]
            users_to_remove.append(sid)
        else:
            print(sid_to_user_id[sid] + ' is still online')
    for user_sid in users_to_remove:
        del sid_to_last_online_msg[user_sid]


check_if_users_are_still_online()

if __name__ == '__main__':
    socketio.run(app, host=conf['HOST'], port=conf['PORT'])
