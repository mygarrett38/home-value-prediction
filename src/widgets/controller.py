from itertools import cycle

from PySide6.QtCore import (
    Qt,
    QObject,
    Signal,
    Slot,
    QByteArray,
    QTimer,
    QPropertyAnimation
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QMainWindow,
    QStackedWidget, 
    QLabel,
    QPushButton, 
    QDoubleSpinBox, 
    QListWidget, 
    QListWidgetItem,
    QMessageBox,
    QGraphicsOpacityEffect
)
from PySide6.QtGui import QPalette

from typing import TypeVar
PlaceholderType = TypeVar("PlaceholderType", bound=QObject)

class Cycler():
    def __init__(self, listlike: list):
        self.cycle = cycle(listlike)
        self.current = None

    def __next__(self) -> object:
        self.current = next(self.cycle)
        return self.current

    def currentValue(self): return self.current

class Controller(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        title_label = QLabel("Home Value Prediction", alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)


    def getWidgetChild(self, child_type: type[PlaceholderType], name: str) -> PlaceholderType:
        widget = self.mainWindow.findChild(child_type, name=name, options=Qt.FindChildOption.FindChildrenRecursively)
        if widget is None: raise ValueError(f"Child \"{name}\" was not found in this window!")
        return widget

    def setMainWindow(self, window: QWidget):
        if hasattr(self, "mainWindow"): return

        self.mainWindow = window
        self.pages = self.getWidgetChild(QStackedWidget, "pages")
        self.form = self.getWidgetChild(QStackedWidget, "pages_form")
        self.form.setCurrentIndex(0)

        self.buttonPredictionBack = self.getWidgetChild(QPushButton, "button_back")
        self.buttonPredictionNext = self.getWidgetChild(QPushButton, "button_next")

        self.pages.setCurrentIndex(0)
    
    @Slot(bool)
    def settingsRequested(self, on: bool):
        self.pages.setCurrentIndex(int(on))

    @Slot()
    def predictionBackClicked(self):
        index = self.form.currentIndex()
        if index == 0: return

        index -= 1
        self.form.setCurrentIndex(index)

        self.buttonPredictionNext.setEnabled(True)
        if index == 0: self.buttonPredictionBack.setEnabled(False)

    @Slot()
    def predictionNextClicked(self):
        index = self.form.currentIndex()
        if index == self.form.count() - 1: return

        index += 1
        self.form.setCurrentIndex(index)

        self.buttonPredictionBack.setEnabled(True)
        if index == self.form.count() - 1: self.buttonPredictionNext.setEnabled(False)
