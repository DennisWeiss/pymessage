from PyQt5.QtWidgets import QLineEdit, QVBoxLayout, QPushButton


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

    layout.addWidget(register_username_field)
    layout.addWidget(register_password_field)
    layout.addWidget(register_password_repeat_field)
    layout.addWidget(register_btn)

    window.setLayout(layout)
