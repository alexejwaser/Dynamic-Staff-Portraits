# app/main.py
import sys
from PySide6 import QtWidgets, QtGui
from pathlib import Path
from app.core.config.settings import Settings
from pydantic import ValidationError
from app.core.util.logging import setup_logging
from app.core.controller import MainController
from app.ui.main_window import MainWindow

def main():
    try:
        settings = Settings.load()
    except ValidationError as e:
        print(f"Fehler in der Konfiguration: {e}", file=sys.stderr)
        return 1
    setup_logging(Path('logs'))
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QtGui.QFont("Segoe UI", 10))
    controller = MainController(settings)
    win = MainWindow(settings, controller)
    win.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
