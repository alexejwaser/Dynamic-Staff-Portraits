# app/main.py
import sys
from PySide6 import QtWidgets, QtGui
from pathlib import Path
import logging
from app.core.config.settings import Settings
from app.core.util.logging import setup_logging
from app.ui.main_window import MainWindow

def main():
    setup_logging(Path('logs'))
    settings = Settings.load()
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QtGui.QFont("Segoe UI", 10))
    win = MainWindow(settings, logging.getLogger(__name__))
    win.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
