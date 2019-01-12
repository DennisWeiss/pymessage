from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QLabel
from socketIO_client import SocketIO, LoggingNamespace
import json
import web_sockets
import session


socket_io = web_sockets.socket_io()

with open('conf.json', encoding='utf-8') as f:
    conf = json.loads(f.read())


def set_up_warning_dialog(window, message):
    layout = QVBoxLayout()

    message_lbl = QLabel(message)
    ok_btn = QPushButton('OK')
    ok_btn.clicked.connect(window.close)

    layout.addWidget(message_lbl)
    layout.addWidget(ok_btn)

    window.setLayout(layout)


def add_friend(friend):
    friends.append(friend)
    file = open(conf['FRIENDS_FILE_NAME'], 'a')
    file.write(friend + '\n')
    file.close()


def add_friend_to_overview(friend, overview):
    friend_widget = QLabel()
    friend_widget.setText(friend)
    overview.addWidget(friend_widget)
    friends_ui.append(friend_widget)


def add_user(username, friends_overview):
    if username == _user_id:
        warning_dialog_window = QWidget()
        set_up_warning_dialog(warning_dialog_window, 'You can\'t add yourself as friend.')
        warning_dialog_window.show()
    response = session_obj.get(
        url=conf['SERVER_ADDRESS'] + '/user',
        params={
            'id': username
        }
    )
    if response.status_code == 200:
        add_friend(username)
        add_friend_to_overview(username, friends_overview)
    elif response.status_code == 404:
        warning_dialog_window = QWidget()
        set_up_warning_dialog(warning_dialog_window, 'User ' + username + ' not found')
        warning_dialog_window.show()


def setup_chat_window(window, user_id, auth_token):
    global _user_id
    global _auth_token
    _user_id = user_id
    _auth_token = auth_token

    socket_io.emit('joining', json.dumps({
        'user_id': user_id,
        'auth_token': auth_token
    }))

    layout = QHBoxLayout()

    user_overview = QVBoxLayout()
    messaging_view = QVBoxLayout()

    friends_overview = QVBoxLayout()

    for friend in friends:
        if friend != user_id:
            add_friend_to_overview(friend, friends_overview)

    add_user_field = QLineEdit()
    add_user_btn = QPushButton('Add User')
    add_user_btn.clicked.connect(lambda: add_user(add_user_field.text(), friends_overview))

    user_overview.addWidget(add_user_field)
    user_overview.addWidget(add_user_btn)
    user_overview.addLayout(friends_overview)

    layout.addLayout(user_overview)
    layout.addLayout(messaging_view)

    window.setLayout(layout)


def read_friends_from_file(file_name):
    file = open(file_name, 'r')
    friends = list(map(lambda string: string.rstrip(), file.readlines()))
    file.close()
    return friends


@socket_io.on('new_user')
def on_new_user_online(user):
    print(user + ' has come online')


session_obj = session.get_session()

friends_file_name = conf['FRIENDS_FILE_NAME']

friends = read_friends_from_file(friends_file_name)
friends_ui = []

_user_id = None
_auth_token = None

warning_dialog = None

