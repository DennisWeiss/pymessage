from PyQt5.QtWidgets import QApplication, QWidget
import login


app = QApplication([])
login_window = QWidget()
login.setup_login_window(login_window)
login_window.show()
app.exec_()
