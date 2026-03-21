from itertools import cycle

from widgets.propertyDisplay import PropertyDisplayManager
from property import STATE_DICT

from PySide6.QtCore import (
    QEvent,
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
    QTableWidget, 
    QLabel,
    QPushButton, 
    QComboBox,
    QDoubleSpinBox, 
    QMessageBox,
    QGraphicsOpacityEffect
)
from PySide6.QtGui import QPalette

from typing import TypeVar
PlaceholderType = TypeVar("PlaceholderType", bound=QObject)

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
        self.mainWindow.installEventFilter(self)

        self.settingsButton = self.getWidgetChild(QPushButton, "settings_button")
        self.pages = self.getWidgetChild(QStackedWidget, "pages")
        self.form = self.getWidgetChild(QStackedWidget, "pages_form")
        self.form.setCurrentIndex(0)

        self.predictionTable = self.getWidgetChild(QTableWidget, "prediction_table")
        self.setTableAlignment()

        self.historyButtons = self.getWidgetChild(QWidget, "history_buttons")
        self.addButton = self.getWidgetChild(QPushButton, "button_history_add")
        self.editButton = self.getWidgetChild(QPushButton, "button_history_edit")
        self.deleteButton = self.getWidgetChild(QPushButton, "button_history_delete")
        self.deleteButton.setVisible(False)

        self.propertyManager = self.getWidgetChild(PropertyDisplayManager, "history_scroll_widget")
        self.propertyManager.connectButton(self.addButton, type="add")
        self.propertyManager.connectButton(self.editButton, type="edit")
        self.propertyManager.connectButton(self.deleteButton, type="remove")

        self.buttonPredictionBack = self.getWidgetChild(QPushButton, "button_back")
        self.buttonPredictionNext = self.getWidgetChild(QPushButton, "button_next")
        self.buttonPredictionStart = self.getWidgetChild(QPushButton, "button_predict_start")
        self.buttonPredictionStart.setVisible(False)

        self.editorLocationState = self.getWidgetChild(QComboBox, "editor_location_state")
        self.editorLocationState.clear()
        self.editorLocationState.addItems(list(STATE_DICT.values()))

        self.pages.setCurrentIndex(1)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        match event.type():
            case QEvent.Type.Resize:
                self.setTableAlignment()
                
            case QEvent.Type.ChildRemoved: # Prevent errors with premature Python garbage collection
                return True        

        return super().eventFilter(watched, event)

    def setTableAlignment(self):
        col_remaining_count = self.predictionTable.columnCount() - 1
        col_width = self.predictionTable.width()
        self.predictionTable.setColumnWidth(0, col_width * 1 // 3)
        for i in range(col_remaining_count):
            self.predictionTable.setColumnWidth(i + 1, col_width * 2 // (3 * col_remaining_count))

        #for i in range(self.predictionTable.rowCount()):
        #    self.predictionTable.setRowHeight(i, self.predictionTable.height() // 7)
    
    @Slot(bool)
    def settingsRequested(self, on: bool):
        self.pages.setCurrentIndex(2 if on else 1)
        self.addButton.setVisible(not on)
        self.editButton.setVisible(not on)
        self.deleteButton.setVisible(on)

    @Slot()
    def addClicked(self):
        self.pages.setCurrentIndex(0)
        self.settingsButton.setEnabled(False)
        self.historyButtons.hide()

    @Slot()
    def editClicked(self):
        self.pages.setCurrentIndex(0)
        self.settingsButton.setEnabled(False)
        self.historyButtons.hide()

    @Slot()
    def deleteClicked(self):
        self.pages.setCurrentIndex(0)

    @Slot()
    def predictionBackClicked(self):
        index = self.form.currentIndex()
        if index == 0:
            self.pages.setCurrentIndex(1)
            self.settingsButton.setEnabled(True)
            self.historyButtons.show()
            return

        index -= 1
        self.form.setCurrentIndex(index)

        self.buttonPredictionStart.setVisible(False)
        self.buttonPredictionNext.setVisible(True)

    @Slot()
    def predictionNextClicked(self):
        index = self.form.currentIndex()
        if index == self.form.count() - 1: return

        index += 1
        self.form.setCurrentIndex(index)

        if index == self.form.count() - 1:
            self.buttonPredictionStart.setVisible(True)
            self.buttonPredictionNext.setVisible(False)

    @Slot()
    def predictionStartClicked(self):
        self.form.setCurrentIndex(0)
        self.pages.setCurrentIndex(1)
        self.settingsButton.setEnabled(True)
        self.buttonPredictionStart.setVisible(False)
        self.buttonPredictionNext.setVisible(True)
        self.historyButtons.show()
