from itertools import cycle

from config import Configuration
from property import Property
from location import Location, STATE_DICT
from widgets.propertyDisplay import PropertyDisplayManager

from PySide6.QtCore import (
    QEvent,
    Qt,
    QObject,
    Signal,
    Slot,
    QDate,
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
    QSpinBox,
    QDoubleSpinBox,
    QLineEdit,
    QDateEdit,
    QMessageBox,
    QGraphicsOpacityEffect
)
from PySide6.QtGui import QPalette

from typing import TypeVar
PlaceholderType = TypeVar("PlaceholderType", bound=QObject)

class Controller(QWidget):
    requestPrediction = Signal(Property)
    requestLocations = Signal(Property)

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        title_label = QLabel("Home Value Prediction", alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        self.currentProperty: Property | None = None

    def getWidgetChild(self, child_type: type[PlaceholderType], name: str) -> PlaceholderType:
        widget = self.mainWindow.findChild(child_type, name=name, options=Qt.FindChildOption.FindChildrenRecursively)
        if widget is None: raise ValueError(f"Child \"{name}\" was not found in this window!")
        return widget
    
    def setConfiguration(self, config: Configuration):
        self.configuration = config

    def setMainWindow(self, window: QWidget):
        if hasattr(self, "mainWindow"): return

        self.mainWindow = window
        self.mainWindow.installEventFilter(self)

        # VISUALIZATION WIDGETS #
        self.settingsButton = self.getWidgetChild(QPushButton, "settings_button")
        self.pages = self.getWidgetChild(QStackedWidget, "pages")
        self.form = self.getWidgetChild(QStackedWidget, "pages_form")
        self.form.setCurrentIndex(0)

        self.predictionTable = self.getWidgetChild(QTableWidget, "prediction_table")
        self.setTableAlignment()

        # PROPERTY MANAGER WIDGETS #
        self.historyButtons = self.getWidgetChild(QWidget, "history_buttons")
        self.addButton = self.getWidgetChild(QPushButton, "button_history_add")
        self.editButton = self.getWidgetChild(QPushButton, "button_history_edit")
        self.deleteButton = self.getWidgetChild(QPushButton, "button_history_delete")
        self.deleteButton.setVisible(False)

        self.propertyManager = self.getWidgetChild(PropertyDisplayManager, "history_scroll_widget")
        self.propertyManager.setConfiguration(self.configuration)
        self.propertyManager.refreshWidgets()
        self.propertyManager.propertySelected.connect(self.currentPropertyChanged)

        # PREDICTION FORM WIDGETS #
        self.buttonPredictionBack = self.getWidgetChild(QPushButton, "button_back")
        self.buttonPredictionNext = self.getWidgetChild(QPushButton, "button_next")
        self.buttonPredictionStart = self.getWidgetChild(QPushButton, "button_predict_start")
        self.buttonPredictionStart.setVisible(False)

        self.editorLocationState = self.getWidgetChild(QComboBox, "editor_location_state")
        self.editorLocationState.clear()
        self.editorLocationState.addItems(list(STATE_DICT.values()))
        self.editorLocationAddress = self.getWidgetChild(QLineEdit, "editor_location_address")

        self.editorPropertyType = self.getWidgetChild(QComboBox, "editor_property_type")
        self.editorPropertyAcreage = self.getWidgetChild(QDoubleSpinBox, "editor_property_acreage")
        self.editorPropertyYear = self.getWidgetChild(QDateEdit, "editor_property_year")
        self.editorPropertyTax = self.getWidgetChild(QDoubleSpinBox, "editor_property_tax_annual")

        self.editorHomeFootage = self.getWidgetChild(QSpinBox, "editor_home_footage")
        self.editorHomeFloors = self.getWidgetChild(QSpinBox, "editor_home_floors")
        self.editorHomeBeds = self.getWidgetChild(QSpinBox, "editor_home_bedrooms")
        self.editorHomeBaths = self.getWidgetChild(QSpinBox, "editor_home_bathrooms")
        self.editorHomeHalfBaths = self.getWidgetChild(QSpinBox, "editor_home_halfbaths")

        self.buttonHomeHeat = self.getWidgetChild(QPushButton, "button_home_heat")
        self.editorHomeHeat = self.getWidgetChild(QComboBox, "editor_home_heat")
        self.buttonHomeAir = self.getWidgetChild(QPushButton, "button_home_ac")
        self.buttonHomeGarage = self.getWidgetChild(QPushButton, "button_home_garage")
        self.editorHomeGarage = self.getWidgetChild(QSpinBox, "editor_home_garage")

        # STARTUP #
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

    @Slot(Property)
    def currentPropertyChanged(self, prop: Property | None):
        self.currentProperty = prop
        self.deleteButton.setEnabled(prop is not None)

    @Slot()
    def addClicked(self):
        self.pages.setCurrentIndex(0)
        self.settingsButton.setEnabled(False)
        self.historyButtons.hide()

        self.currentProperty = Property()
        self.propertyManager.addProperty(self.currentProperty)
        self.setPropertyEditors()

    @Slot()
    def editClicked(self):
        self.pages.setCurrentIndex(0)
        self.settingsButton.setEnabled(False)
        self.historyButtons.hide()

        self.setPropertyEditors()

    @Slot()
    def deleteClicked(self):
        if QMessageBox.question(self, "Are you sure?", "This property and its prediction will be permanently deleted.\n\nAre you sure you want to do this?") == QMessageBox.StandardButton.No: return
        self.configuration.removeProperty(self.propertyManager.currentPropIndex)
        self.propertyManager.removeProperty()

    def setPropertyEditors(self):
        if self.currentProperty is None: raise ValueError("setPropertyEditors(): No current property!")

        self.editorLocationState.setCurrentIndex(self.currentProperty.location_state)
        self.editorLocationAddress.setText(self.currentProperty.location_address)

        self.editorPropertyType.setCurrentText(self.currentProperty.prop_type)
        self.editorPropertyAcreage.setValue(self.currentProperty.acreage)
        self.editorPropertyYear.setDate(QDate(self.currentProperty.year_built, 1, 1))
        self.editorPropertyTax.setValue(self.currentProperty.tax_annual)

        self.editorHomeFootage.setValue(self.currentProperty.square_feet)
        self.editorHomeFloors.setValue(self.currentProperty.floors)
        self.editorHomeBeds.setValue(self.currentProperty.beds)
        self.editorHomeBaths.setValue(self.currentProperty.baths)
        self.editorHomeHalfBaths.setValue(self.currentProperty.baths_half)

        self.buttonHomeHeat.setChecked(self.currentProperty.sys_heat is not None)
        self.editorHomeHeat.setCurrentText("Central" if self.currentProperty.sys_heat is None else self.currentProperty.sys_heat)
        self.buttonHomeAir.setChecked(self.currentProperty.sys_ac)
        self.buttonHomeGarage.setChecked(self.currentProperty.garages > 0)
        self.editorHomeGarage.setValue(max(self.currentProperty.garages, 1))

    def getPropertyEditors(self):
        return Property(
            price=0,

            location_state=self.editorLocationState.currentIndex(),
            location_address=self.editorLocationAddress.text(),

            prop_type=self.editorPropertyType.currentText(),
            acreage=self.editorPropertyAcreage.value(),
            year_built=self.editorPropertyYear.date().year(),
            tax_annual=self.editorPropertyTax.value(),

            square_feet=self.editorHomeFootage.value(),
            floors=self.editorHomeFloors.value(),
            beds=self.editorHomeBeds.value(),
            baths=self.editorHomeBaths.value(),
            baths_half=self.editorHomeHalfBaths.value(),

            sys_heat=self.editorHomeHeat.currentText() if self.buttonHomeHeat.isChecked() else None,
            sys_ac=self.buttonHomeAir.isChecked(),
            garages=self.editorHomeGarage.value() if self.buttonHomeGarage.isChecked() else 0
        )

    @Slot()
    def predictionBackClicked(self):
        index = self.form.currentIndex()
        if index == 0:
            self.pages.setCurrentIndex(1)
            self.settingsButton.setEnabled(True)
            self.historyButtons.show()
            self.propertyManager.removeProperty()
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
        self.requestPrediction.emit(self.getPropertyEditors())

    @Slot()
    def locationRequested(self):
        if self.currentProperty is None: raise ValueError("locationRequested(): No Property to request!")
        self.currentProperty = self.getPropertyEditors()
        self.requestLocations.emit(self.currentProperty)

    @Slot(list)
    def locationsProcessed(self, locations: list[Location]):
        print([l.getCoordinates() for l in locations])

    @Slot(Property)
    def predictionProcessed(self, prop: Property):
        self.currentProperty = prop

        self.form.setCurrentIndex(0)
        self.pages.setCurrentIndex(1)
        self.settingsButton.setEnabled(True)
        self.buttonPredictionStart.setVisible(False)
        self.buttonPredictionNext.setVisible(True)
        self.historyButtons.show()

        print(prop.price)
