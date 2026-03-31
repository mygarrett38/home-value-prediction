from typing import Literal
from itertools import cycle

from config import Configuration, GraphMode, TableMode
from property import Property
from location import Location
from widgets.propertyDisplay import PropertyDisplayManager
from widgets.graph import GraphDisplay

from PySide6.QtCore import (
    QEvent,
    Qt,
    QObject,
    QMetaObject,
    Signal,
    Slot,
    QDate,
    QTimer,
    QPropertyAnimation,
    QItemSelectionModel
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QStackedWidget, 
    QTableWidget, 
    QTableWidgetItem, 
    QHeaderView,
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

TABLE_COLUMN_NAMES = {
    TableMode.PREDICTION_RANGE: ("Home Address", "Prediction", "Lower Bound", "Upper Bound"),
    TableMode.PROPERTY_INFO: ("Home Address", "Prediction", "Year Built", "Type", "Acreage", "Annual Tax"),
    TableMode.HOME_INFO: ("Home Address", "Prediction", "Sq. Ft.", "Beds", "Baths", "Floors", "Basement", "Heating", "Garages")
}

def propertyNameToValue(name: str, prop: Property):
    match name:
        case "Home Address": return f" {prop.location.address}"
        case "Prediction": return f"${round(prop.price, -2):,.0f}"
        case "Lower Bound": return f"${round(prop.price * 0.835, -2):,.0f}"
        case "Upper Bound": return f"${round(prop.price * 1.18, -2):,.0f}"
        case "Year Built": return str(prop.year_built)
        case "Type": return prop.prop_type
        case "Acreage": return f"{prop.acreage:.3f}"
        case "Annual Tax": return f"${prop.tax_annual:,.2f}"
        case "Sq. Ft.": return str(prop.square_feet)
        case "Beds": return str(prop.beds)
        case "Baths": return str(prop.totalBaths())
        case "Floors": return str(prop.floors)
        case "Basement": return prop.basement
        case "Heating": return prop.heat
        case "Garages": return str(prop.garages)
        case _: return ""

class Controller(QWidget):
    requestPrediction = Signal(Property)
    requestLocation = Signal(Property)
    requestInfo = Signal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        title_label = QLabel("Home Value Prediction", alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        self.cyclerVisualizationRange = cycle(GraphMode)
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
        self.buttonGraphMode = self.getWidgetChild(QPushButton, "graph_mode_button")
        self.pages = self.getWidgetChild(QStackedWidget, "pages")
        self.form = self.getWidgetChild(QStackedWidget, "pages_form")
        self.form.setCurrentIndex(0)

        self.predictionGraph = self.getWidgetChild(GraphDisplay, "graph")
        self.predictionGraph.setConfiguration(self.configuration)
        self.predictionTable = self.getWidgetChild(QTableWidget, "prediction_table")
        self.predictionTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.refreshTable()

        # PROPERTY MANAGER WIDGETS #
        self.historyButtons = self.getWidgetChild(QWidget, "history_buttons")
        self.addButton = self.getWidgetChild(QPushButton, "button_history_add")
        self.editButton = self.getWidgetChild(QPushButton, "button_history_edit")
        self.deleteButton = self.getWidgetChild(QPushButton, "button_history_delete")

        self.propertyManager = self.getWidgetChild(PropertyDisplayManager, "history_scroll_widget")
        self.propertyManager.setConfiguration(self.configuration)
        self.propertyManager.refreshWidgets()
        self.propertyManager.propertySelected.connect(self.currentPropertyChanged)

        # PREDICTION FORM WIDGETS #
        self.buttonPredictionBack = self.getWidgetChild(QPushButton, "button_back")
        self.buttonPredictionNext = self.getWidgetChild(QPushButton, "button_next")
        self.buttonPredictionStart = self.getWidgetChild(QPushButton, "button_predict_start")
        self.buttonPredictionStart.setVisible(False)

        self.editorLocationZipCode = self.getWidgetChild(QLineEdit, "editor_location_zip")
        self.editorLocationAddress = self.getWidgetChild(QLineEdit, "editor_location_address")
        self.labelLocationMap = self.getWidgetChild(QLabel, "label_location_map")
        self.buttonLocationZoomIn = self.getWidgetChild(QPushButton, "button_location_zoom_in")
        self.buttonLocationZoomOut = self.getWidgetChild(QPushButton, "button_location_zoom_out")

        self.editorPropertyType = self.getWidgetChild(QComboBox, "editor_property_type")
        self.editorPropertyAcreage = self.getWidgetChild(QDoubleSpinBox, "editor_property_acreage")
        self.editorPropertyYear = self.getWidgetChild(QDateEdit, "editor_property_year")
        self.editorPropertyTax = self.getWidgetChild(QDoubleSpinBox, "editor_property_tax_annual")

        self.editorHomeFootage = self.getWidgetChild(QSpinBox, "editor_home_footage")
        self.editorHomeBeds = self.getWidgetChild(QSpinBox, "editor_home_bedrooms")
        self.editorHomeBaths = self.getWidgetChild(QSpinBox, "editor_home_bathrooms")
        self.editorHomeHalfBaths = self.getWidgetChild(QSpinBox, "editor_home_halfbaths")

        self.editorHomeFloors = self.getWidgetChild(QSpinBox, "editor_home_floors")
        self.editorHomeBasement = self.getWidgetChild(QComboBox, "editor_home_basement")
        self.editorHomeHeat = self.getWidgetChild(QComboBox, "editor_home_heat")
        self.editorHomeGarage = self.getWidgetChild(QSpinBox, "editor_home_garage")

        # STARTUP #
        if len(self.configuration) == 0:
            self.addClicked()
            self.buttonPredictionBack.setVisible(False)
        else:
            self.pages.setCurrentIndex(1)

        currentGraphMode = self.configuration.graphMode
        self.visualizeModeClicked()
        while currentGraphMode != self.configuration.graphMode:
            self.visualizeModeClicked()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        match event.type():
            case QEvent.Type.Resize:
                self.setTableAlignment()
                
            case QEvent.Type.ChildRemoved: # Prevent errors with premature Python garbage collection
                return True        

        return super().eventFilter(watched, event)

    @Slot()
    def setTableAlignment(self):
        col_remaining_count = self.predictionTable.columnCount() - 1
        col_width = self.predictionTable.width()
        self.predictionTable.setColumnWidth(0, col_width * 1 // 3)
        for i in range(col_remaining_count):
            self.predictionTable.setColumnWidth(i + 1, col_width * 2 // (3 * col_remaining_count))

    def refreshTable(self):
        tableMode = self.configuration.tableMode

        self.predictionTable.clear()

        self.predictionTable.setColumnCount(len(TABLE_COLUMN_NAMES[tableMode]))
        self.predictionTable.setHorizontalHeaderLabels(TABLE_COLUMN_NAMES[tableMode])

        self.predictionTable.setRowCount(len(self.configuration))
        for i, prop in enumerate(self.configuration):
            for j, col in enumerate(TABLE_COLUMN_NAMES[tableMode]):
                item = QTableWidgetItem(propertyNameToValue(col, prop))
                if j > 0: item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                font = item.font()
                font.setBold(self.currentProperty == prop)
                item.setFont(font)
                self.predictionTable.setItem(i, j, item)

            if self.currentProperty == prop:
                self.predictionTable.selectionModel().select(
                    self.predictionTable.model().index(i, 0),
                    QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows
                )

        QMetaObject.invokeMethod(self, "setTableAlignment", Qt.ConnectionType.QueuedConnection) # type: ignore
    
    def setView(self, view: Literal["prediction", "graph"]):
        visualizeViewed = view == "graph"

        self.pages.setCurrentIndex(1 if visualizeViewed else 0)
        self.buttonGraphMode.setEnabled(visualizeViewed)
        self.historyButtons.setVisible(visualizeViewed)

        if visualizeViewed:
            self.propertyManager.setPredictionInProgress(-1)

    @Slot(bool)
    def settingsRequested(self, on: bool):
        self.pages.setCurrentIndex(2 if on else 1)
        self.addButton.setVisible(not on)
        self.editButton.setVisible(not on)
        self.deleteButton.setVisible(on)

    @Slot()
    def infoClicked(self):
        self.requestInfo.emit()

    @Slot()
    def visualizeModeClicked(self):
        newMode = next(self.cyclerVisualizationRange)

        self.configuration.graphMode = newMode
        self.configuration.tableMode = list(TableMode.__members__.values())[list(GraphMode.__members__.values()).index(newMode)]
        self.buttonGraphMode.setText(newMode.value)

        self.predictionGraph.refresh(self.currentProperty)
        self.refreshTable()

    @Slot(Property)
    def currentPropertyChanged(self, prop: Property | None):
        self.currentProperty = prop
        self.editButton.setEnabled(prop is not None)
        self.deleteButton.setEnabled(prop is not None and len(self.configuration) > 1)
        self.predictionGraph.refresh(self.currentProperty)
        self.refreshTable()

    @Slot()
    def addClicked(self):
        self.setView("prediction")
        self.buttonPredictionNext.setEnabled(False)

        self.currentProperty = Property()
        self.propertyManager.addProperty(self.currentProperty)
        self.setPropertyEditors()

    @Slot()
    def editClicked(self):
        self.setView("prediction")
        self.buttonPredictionNext.setEnabled(True)

        if self.currentProperty.location.getCoordinates() != (0.0, 0.0) and self.currentProperty.location.getMapImage().isNull(): # type: ignore
            self.requestLocation.emit(self.currentProperty)

        self.propertyManager.setPredictionInProgress(self.propertyManager.currentPropIndex)
        self.setPropertyEditors()

    @Slot()
    def deleteClicked(self):
        if QMessageBox.question(self, "Are you sure?", "This property and its prediction will be permanently deleted.\n\nAre you sure you want to do this?") == QMessageBox.StandardButton.No: return
        self.configuration.removeProperty(self.propertyManager.currentPropIndex)
        self.propertyManager.removeProperty()

        self.predictionGraph.refresh(self.currentProperty)
        self.refreshTable()

    def setPropertyEditors(self):
        if self.currentProperty is None: raise ValueError("setPropertyEditors(): No current property!")

        self.editorLocationZipCode.setText(self.currentProperty.location.getZipCode())
        self.editorLocationAddress.setText(self.currentProperty.location.getAddress())
        if self.currentProperty.location.getMapImage().isNull():
            self.labelLocationMap.setText("The location of the home will appear here.")
            self.buttonLocationZoomIn.setEnabled(False)
            self.buttonLocationZoomOut.setEnabled(False)
        else:
            self.labelLocationMap.setPixmap(self.currentProperty.location.getMapImage())
            self.buttonLocationZoomIn.setEnabled(True)
            self.buttonLocationZoomOut.setEnabled(True)
        
        self.editorPropertyType.setCurrentText(self.currentProperty.prop_type)
        self.editorPropertyAcreage.setValue(self.currentProperty.acreage)
        self.editorPropertyYear.setDate(QDate(self.currentProperty.year_built, 1, 1))
        self.editorPropertyTax.setValue(self.currentProperty.tax_annual)

        self.editorHomeFootage.setValue(self.currentProperty.square_feet)
        self.editorHomeBeds.setValue(self.currentProperty.beds)
        self.editorHomeBaths.setValue(self.currentProperty.baths)
        self.editorHomeHalfBaths.setValue(self.currentProperty.baths_half)

        self.editorHomeFloors.setValue(self.currentProperty.floors)
        self.editorHomeBasement.setCurrentText(self.currentProperty.basement)
        self.editorHomeHeat.setCurrentText(self.currentProperty.heat)
        self.editorHomeGarage.setValue(self.currentProperty.garages)

    def getPropertyEditors(self):
        if self.currentProperty is None: raise ValueError("getPropertyEditors(): No property to set to!")

        zip_address = Location(self.editorLocationZipCode.text(), self.editorLocationAddress.text())
        if self.currentProperty.location != zip_address:
            self.currentProperty.location = zip_address

        self.currentProperty.prop_type = self.editorPropertyType.currentText()
        self.currentProperty.acreage = self.editorPropertyAcreage.value()
        self.currentProperty.year_built = self.editorPropertyYear.date().year()
        self.currentProperty.tax_annual = self.editorPropertyTax.value()

        self.currentProperty.square_feet = self.editorHomeFootage.value()
        self.currentProperty.beds = self.editorHomeBeds.value()
        self.currentProperty.baths = self.editorHomeBaths.value()
        self.currentProperty.baths_half = self.editorHomeHalfBaths.value()

        self.currentProperty.floors = self.editorHomeFloors.value()
        self.currentProperty.basement = self.editorHomeBasement.currentText()
        self.currentProperty.heat = self.editorHomeHeat.currentText()
        self.currentProperty.garages = self.editorHomeGarage.value()

    @Slot()
    def predictionBackClicked(self):
        index = self.form.currentIndex()
        if index == 0:
            self.setView("graph")
            
            if self.currentProperty not in self.configuration:
                self.propertyManager.removeProperty()
                self.currentPropertyChanged(None)
            
            return
        elif index == 1 and len(self.configuration) == 0:
            self.buttonPredictionBack.setVisible(False)

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
        self.getPropertyEditors()
        self.propertyManager.refreshCurrentAttributes()

        self.buttonPredictionBack.setVisible(True)
        if index == self.form.count() - 1:
            self.buttonPredictionStart.setVisible(True)
            self.buttonPredictionNext.setVisible(False)

    @Slot()
    def predictionStartClicked(self):
        self.getPropertyEditors()
        self.requestPrediction.emit(self.currentProperty)

    @Slot()
    def zoomInClicked(self):
        if self.currentProperty is None: raise ValueError("zoomInClicked(): No Property to request!")

        self.currentProperty.location.zoomLevel += 1
        self.locationRequested()

    @Slot()
    def zoomOutClicked(self):
        if self.currentProperty is None: raise ValueError("zoomOutClicked(): No Property to request!")

        self.currentProperty.location.zoomLevel -= 1
        self.locationRequested()

    @Slot()
    def locationRequested(self):
        if self.currentProperty is None: raise ValueError("locationRequested(): No Property to request!")

        self.labelLocationMap.setText("The location of the home will appear here.")
        self.getPropertyEditors()
        self.requestLocation.emit(self.currentProperty)

    @Slot()
    def locationProcessed(self):
        if self.currentProperty is None: raise ValueError("locationProcessed(): No Property to process!")
        if self.currentProperty.location.getCoordinates() == (0.0, 0.0): return

        self.labelLocationMap.setPixmap(self.currentProperty.location.getMapImage())
        self.buttonLocationZoomIn.setEnabled(True)
        self.buttonLocationZoomOut.setEnabled(True)
        self.buttonPredictionNext.setEnabled(True)

        self.propertyManager.refreshCurrentAttributes()

    @Slot(Property)
    def predictionProcessed(self, prop: Property):
        self.currentPropertyChanged(prop)
        self.propertyManager.refreshCurrentAttributes()

        self.setView("graph")
        self.form.setCurrentIndex(0)
        self.buttonPredictionStart.setVisible(False)
        self.buttonPredictionNext.setVisible(True)
