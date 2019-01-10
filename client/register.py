from PyQt5.QtWidgets import QLineEdit, QVBoxLayout, QPushButton
import session
import json


with open('conf.json', encoding='utf-8') as f:
    conf = json.loads(f.read())

session_obj = session.get_session()


def passwords_do_not_match():
    # TODO: show info to user
    print('Passwords do not match.')


def register(username, password, password_repeat):
    if password != password_repeat:
        passwords_do_not_match()
    else:
        response = session_obj.post(
            url=conf['SERVER_ADDRESS'] + '/register',
            json={
                'user_id': username,
                'password': password
            }
        )
        print(response.text)


def setup_register_window(window):
    layout = QVBoxLayout()

    register_username_field = QLineEdit()
    register_username_field.setPlaceholderText('Username')

    register_password_field = QLineEdit()
    register_password_field.setPlaceholderText('Password')
    register_password_field.setEchoMode(QLineEdit.Password)

    register_password_repeat_field = QLineEdit()
    register_password_repeat_field.setPlaceholderText('Repeat Password')
    register_password_repeat_field.setEchoMode(QLineEdit.Password)

    register_btn = QPushButton('Register')
    register_btn.clicked.connect(lambda: register(register_username_field.text(), register_password_field.text(),\
                                                  register_password_repeat_field.text()))

    layout.addWidget(register_username_field)
    layout.addWidget(register_password_field)
    layout.addWidget(register_password_repeat_field)
    layout.addWidget(register_btn)

    window.setLayout(layout)
