# app/main.py
import sys
from PySide6 import QtWidgets, QtGui
from pathlib import Path
from app.core.config.settings import Settings
from app.core.util.logging import setup_logging
from app.ui.main_window import MainWindow

def main():
    settings = Settings.load()
    setup_logging(Path('logs'))
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QtGui.QFont("Segoe UI", 10))
    win = MainWindow(settings)
    win.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
