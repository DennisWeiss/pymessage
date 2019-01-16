from PyQt5.QtWidgets import QLineEdit, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
import register
import session
import json
import chat


with open('conf.json', encoding='utf-8') as f:
    conf = json.loads(f.read())

register_window = None
chat_window = None

session_obj = session.get_session()


def login(username, password, login_info_lbl, login_window):
    response = session_obj.post(
        url=conf['SERVER_ADDRESS'] + '/login',
        json={
            'user_id': username,
            'password': password
        }
    )
    if response.status_code == 401:
        login_info_lbl.setText('Wrong password!')
    elif response.status_code == 200:
        data = json.loads(response.text)
        if 'msg' in data:
            login_info_lbl.setText(data['msg'])
        else:
            global chat_window
            chat_window = QWidget()
            chat.setup_chat_window(chat_window, data['user_id'], data['auth_token'])
            chat_window.show()
            login_window.close()


def register_btn_click():
    global register_window
    register_window = QWidget()
    register.setup_register_window(register_window)
    register_window.show()
    


def setup_login_window(window):
    layout = QVBoxLayout()

    login_register_btns = QHBoxLayout()

    register_btn = QPushButton('Register')
    register_btn.clicked.connect(register_btn_click)

    username_login_field = QLineEdit()
    username_login_field.setPlaceholderText('Username')

    password_login_field = QLineEdit()
    password_login_field.setPlaceholderText('Password')
    password_login_field.setEchoMode(QLineEdit.Password)

    login_info = QLabel()

    login_btn = QPushButton('Login')
    login_btn.clicked.connect(lambda: login(username_login_field.text(), password_login_field.text(), login_info, window))

    login_register_btns.addWidget(register_btn)
    login_register_btns.addWidget(login_btn)

    layout.addWidget(username_login_field)
    layout.addWidget(password_login_field)
    layout.addLayout(login_register_btns)
    layout.addWidget(login_info)

    window.setLayout(layout)
