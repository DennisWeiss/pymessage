from PyQt5.QtWidgets import QApplication, QWidget
import login
from PyQt5 import QtGui

app = QApplication(['PyMessage'])
app.setWindowIcon(QtGui.QIcon('icon.png'))
login_window = QWidget()
login.setup_login_window(login_window)
login_window.show()
app.exec_()
