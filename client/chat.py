from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QLabel
from socketIO_client import SocketIO, LoggingNamespace
import json
import web_sockets
import session


socket_io = web_sockets.socket_io()

with open('conf.json', encoding='utf-8') as f:
    conf = json.loads(f.read())

session_obj = session.get_session()

friends = []


def add_user(username, friends_overview):
    response = session_obj.get(
        url=conf['SERVER_ADDRESS'] + '/user',
        params={
            'id': username
        }
    )
    if response.status_code == 200:
        friend = QLabel()
        friend.setText(username)
        friends_overview.addWidget(friend)
        friends.append(friend)


def setup_chat_window(window, user_id, auth_token):
    socket_io.emit('joining', json.dumps({
        'user_id': user_id,
        'auth_token': auth_token
    }))

    layout = QHBoxLayout()

    user_overview = QVBoxLayout()
    messaging_view = QVBoxLayout()

    friends_overview = QVBoxLayout()

    add_user_field = QLineEdit()
    add_user_btn = QPushButton('Add User')
    add_user_btn.clicked.connect(lambda: add_user(add_user_field.text(), friends_overview))

    user_overview.addWidget(add_user_field)
    user_overview.addWidget(add_user_btn)
    user_overview.addLayout(friends_overview)

    layout.addLayout(user_overview)
    layout.addLayout(messaging_view)

    window.setLayout(layout)



