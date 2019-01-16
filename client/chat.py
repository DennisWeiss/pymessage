from PyQt5 import QtCore
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QLabel, QPlainTextEdit, QScrollArea
import json
import web_sockets
import session
from user import User
from message import Message


socket_io = web_sockets.socket_io()

with open('conf.json', encoding='utf-8') as f:
    conf = json.loads(f.read())


class PyQtThread(QThread):
    signal = QtCore.pyqtSignal()


def set_up_warning_dialog(window, message):
    layout = QVBoxLayout()

    message_lbl = QLabel(message)
    ok_btn = QPushButton('OK')
    ok_btn.clicked.connect(window.close)

    layout.addWidget(message_lbl)
    layout.addWidget(ok_btn)

    window.setLayout(layout)


def add_friend(friend):
    response = session_obj.get(
        url=conf['SERVER_ADDRESS'] + '/online',
        params={
            'user': friend
        }
    )
    data = json.loads(response.text)
    friend_user = User(friend)
    friend_user.online = data and data['online']
    friends[friend] = friend_user
    file = open(conf['FRIENDS_FILE_NAME'], 'a')
    file.write(friend + '\n')
    file.close()


def select_friend(username):
    global friend_selected
    friend_selected = username
    for friend_widget in friends_ui:
        if friend_widget.text() == username:
            if friend_widget.text() in friends and friends[friend_widget.text()].online:
                friend_widget.setStyleSheet("QLabel {background-color: rgba(0, 255, 0, 0.2); color: black;}")
            else:
                friend_widget.setStyleSheet("QLabel {background-color: rgba(0, 255, 0, 0.2); color: gray}")
        else:
            if friend_widget.text() in friends and friends[friend_widget.text()].online:
                friend_widget.setStyleSheet("QLabel {background-color: rgba(0,0,0,0); color: black;}")
            else:
                friend_widget.setStyleSheet("QLabel {background-color: rgba(0,0,0,0); color: gray;}")
    update_messages_box()
    print(friend_selected)


def add_friend_to_overview(friend, overview):
    friend_widget = QLabel()
    friend_widget.setText(friend)
    friend_widget.setStyleSheet('color: gray')
    friend_widget.mousePressEvent = lambda e: select_friend(friend)
    overview.addWidget(friend_widget)
    friends_ui.append(friend_widget)


def add_user(username, friends_overview):
    if username == _user_id:
        warning_dialog_window = QWidget()
        set_up_warning_dialog(warning_dialog_window, 'You can\'t add yourself as friend.')
        warning_dialog_window.show()
    else:
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


def send_message(user, message):
    print(user)
    socket_io.emit('message', json.dumps({
        'user_id': user,
        'msg': message,
        'auth_token': _auth_token
    }))
    friends[user].messages.append(Message(_user_id, user, message))
    update_messages_box()


def update_messages_box():
    if friend_selected:
        for i in reversed(range(messages_box.count())):
            messages_box.itemAt(i).widget().setParent(None)
        for message in friends[friend_selected].messages:
            messages_box.addWidget(QLabel('{}: {}'.format(message.sender, message.content)))


def setup_chat_window(window, user_id, auth_token):
    global _user_id
    global _auth_token
    global messages_box
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

    for friend, user in friends.items():
        if friend != user_id:
            add_friend_to_overview(friend, friends_overview)

    add_user_field = QLineEdit()
    add_user_btn = QPushButton('Add User')
    add_user_btn.clicked.connect(lambda: add_user(add_user_field.text(), friends_overview))

    message_text_field = QPlainTextEdit()
    message_text_field.setFixedHeight(40)
    send_btn = QPushButton('Send')
    send_btn.clicked.connect(lambda: send_message(friend_selected, message_text_field.toPlainText()))

    messages_box_scroll_area = QScrollArea()
    messages_box_scroll_area.setWidgetResizable(True)
    messages_box_content = QWidget(messages_box_scroll_area)

    messages_box = QVBoxLayout(messages_box_content)
    update_messages_box()

    messages_box_scroll_area.setWidget(messages_box_content)

    message_box_layout = QHBoxLayout()

    message_box_layout.addWidget(message_text_field)
    message_box_layout.addWidget(send_btn)

    user_overview.addWidget(add_user_field)
    user_overview.addWidget(add_user_btn)
    user_overview.addLayout(friends_overview)

    messaging_view.addWidget(messages_box_scroll_area)
    messaging_view.addLayout(message_box_layout)

    layout.addLayout(user_overview)
    layout.addLayout(messaging_view)

    window.setLayout(layout)


def read_friends_from_file(file_name):
    file = open(file_name, 'r')
    friends = list(map(lambda string: string.rstrip(), file.readlines()))
    file.close()
    friends_dict = {}
    for user_name in friends:
        friend = User(user_name)
        friend.online = False
        friends_dict[user_name] = friend
    return friends_dict


def add_message_to_messages_box(username, message, messages_box):
    messages_box.addWidget(QLabel('{}: {}'.format(username, message)))


@socket_io.on('new_user')
def on_new_user_online(user):
    if user in friends:
        friends[user].online = True
        for friend_widget in friends_ui:
            if friend_widget.text() == user:
                friend_widget.setStyleSheet('color: black')


@socket_io.on('receive_message')
def one_receive_message(json_data):
    data = json.loads(json_data)
    if data['user_id'] in friends:
        friends[data['user_id']].add_message(Message(data['user_id'], _user_id, data['msg']))
        print(list(map(lambda message: message.content, friends[data['user_id']].messages)))
    if data['user_id'] == friend_selected:
        global messages_box
        thread = PyQtThread()
        thread.signal.connect(lambda: add_message_to_messages_box(data['user_id'], data['msg'], messages_box))


session_obj = session.get_session()

friends_file_name = conf['FRIENDS_FILE_NAME']

friends = read_friends_from_file(friends_file_name)
friends_ui = []

friend_selected = None

_user_id = None
_auth_token = None

warning_dialog = None

messages_box = None

