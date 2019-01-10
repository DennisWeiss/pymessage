from PyQt5.QtWidgets import QLineEdit, QVBoxLayout


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

    layout.addWidget(register_username_field)
    layout.addWidget(register_password_field)
    layout.addWidget(register_password_repeat_field)

    window.setLayout(layout)
