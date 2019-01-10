from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget
import login


app = QApplication([])
window = QWidget()
login.setup_login_window(window)
window.show()
app.exec_()
