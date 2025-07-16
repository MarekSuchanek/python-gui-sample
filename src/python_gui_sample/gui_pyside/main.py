import sys

from PySide6.QtWidgets import QApplication, QWidget


def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("PySide6 GUI Sample")
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
