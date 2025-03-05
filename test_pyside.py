import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton

app = QApplication(sys.argv)
window = QMainWindow()
window.setWindowTitle("PySide6 Test")
window.setGeometry(100, 100, 400, 200)

button = QPushButton("Hello PySide6", window)
button.setGeometry(150, 80, 100, 30)

window.show()
sys.exit(app.exec())