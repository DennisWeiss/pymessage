from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QLineEdit, QWidget, QVBoxLayout, QPushButton, QHBoxLayout


def setup_login_window(window):
    layout = QVBoxLayout()

    login_register_btns = QHBoxLayout()

    register_btn = QPushButton('Register')
    login_btn = QPushButton('Login')

    login_register_btns.addWidget(register_btn)
    login_register_btns.addWidget(login_btn)

    username_login_field = QLineEdit()
    username_login_field.setPlaceholderText('Username')

    password_login_field = QLineEdit()
    password_login_field.setPlaceholderText('Password')

    layout.addWidget(username_login_field)
    layout.addWidget(password_login_field)
    layout.addLayout(login_register_btns)

    window.setLayout(layout)
