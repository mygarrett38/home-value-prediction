import sys
import os.path
from datetime import datetime

from widgets.controller import Controller
from widgets.graph import GraphDisplay

from PySide6.QtCore import Qt, QObject, QThread, QTimer, Signal, Slot
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QIcon
from PySide6.QtUiTools import QUiLoader

def absolutePath(relative_path: str):
    return os.path.join(os.path.dirname(__file__), relative_path)

class HomeValueApplication(QApplication):
    def __init__(self, argv: list[str]):
        super().__init__(argv)

        ui_loader = QUiLoader(self)
        ui_loader.registerCustomWidget(Controller)
        ui_loader.registerCustomWidget(GraphDisplay)
        window = ui_loader.load(absolutePath("widgets/home-value-window.ui"))

        self.controller = window.findChild(Controller, name="controller", options=Qt.FindChildOption.FindChildrenRecursively)
        self.controller.setMainWindow(window) # type: ignore

        window.setWindowIcon(QIcon(absolutePath("widgets/icons/refresh.svg")))

        window.showMaximized()
        window.destroyed.connect(self.quit)

if __name__ == "__main__":
    sys.exit(HomeValueApplication(sys.argv).exec())