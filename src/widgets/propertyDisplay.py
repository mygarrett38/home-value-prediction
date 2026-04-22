from PySide6.QtCore import (
    Qt,
    Signal,
    QSignalBlocker
)

from PySide6.QtGui import (
    QMouseEvent,
)
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QMessageBox,
)

from property import Property
from config import Configuration

def resetStylesheet(widget: QWidget):
    ss = widget.styleSheet()
    widget.setStyleSheet("/* */")
    widget.setStyleSheet(ss)


# This holds each property within the interface
# It handles selection as well as properly displaying the property attributes
class PropertyDisplay(QWidget):
    selected = Signal(bool)

    def __init__(self, parent: QWidget, property: Property):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.prop = property
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        self.setLayout(main_layout)

        desc_layout = QVBoxLayout()
        desc_layout.setContentsMargins(0, 0, 0, 0)
        desc_layout.setSpacing(5)
        main_layout.addLayout(desc_layout, stretch=1)

        propFont = self.font()
        propFont.setPointSize(14)
        propFont.setBold(True)

        self.addressLabel = QLabel(property.location.address, parent=self)
        self.addressLabel.setFont(propFont)
        desc_layout.addWidget(self.addressLabel)

        propFont.setPointSize(11)
        propFont.setBold(False)

        self.propertyLabel = QLabel("", parent=self)
        self.propertyLabel.setFont(propFont)
        desc_layout.addWidget(self.propertyLabel)

        propFont.setPointSize(12)
        propFont.setItalic(True)

        self.priceLabel = QLabel("", parent=self, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.priceLabel.setFont(propFont)
        main_layout.addWidget(self.priceLabel)

        self.refreshPropertyAttributes()

    def select(self):
        self.setProperty("selected", 1)
        resetStylesheet(self)
        self.selected.emit(True)

    def deselect(self):
        self.setProperty("selected", 0)
        resetStylesheet(self)
        self.selected.emit(False)

    def isSelected(self):
        return self.property("selected") == 1

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.select() if not self.isSelected() else self.deselect()
        return super().mousePressEvent(event)

    def refreshPropertyAttributes(self):
        self.addressLabel.setText(self.prop.location.address)
        self.propertyLabel.setText(" | ".join(self.prop.attributes()))
        priceText = f"${round(self.prop.price / 1_000_000, 2)}m" if self.prop.price >= 1_000_000 else f"${round(self.prop.price / 1000)}k"
        self.priceLabel.setText(priceText)
        self.setObjectName(self.prop.location.address)


# This class is here to display all the PropertyDisplays in list form
# It also handles selection and editing
class PropertyDisplayManager(QWidget):
    propertySelected = Signal(Property)

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.super_layout = QVBoxLayout()
        self.super_layout.setContentsMargins(10, 10, 10, 10)
        self.super_layout.setSpacing(0)
        self.setLayout(self.super_layout)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.super_layout.addLayout(self.main_layout)
        self.super_layout.addStretch(1)

        self.currentPropIndex = -1
        self.inProgressIndex = -1
    
    def setPredictionInProgress(self, in_progress_index: int):
        self.inProgressIndex = in_progress_index

    def setConfiguration(self, config: Configuration):
        self.configuration = config

    def refreshWidgets(self):
        while self.main_layout.count() > 0:
            item = self.main_layout.takeAt(0)
            item.widget().deleteLater() # type: ignore
            del item

        for property in self.configuration:
            prop_display = PropertyDisplay(self, property)
            prop_display.selected.connect(self.handlePropertySelected)
            self.main_layout.addWidget(prop_display)

    def refreshCurrentAttributes(self):
        currentDisplay: PropertyDisplay = self.main_layout.itemAt(self.currentPropIndex).widget() # type: ignore
        currentDisplay.refreshPropertyAttributes()

    def setCurrentPropertyIndex(self, index: int):
        self.inProgressIndex = -1
        if self.currentPropIndex == index: return

        if 0 <= self.currentPropIndex < len(self.configuration):
            oldWidget: PropertyDisplay = self.main_layout.itemAt(self.currentPropIndex).widget() # type: ignore
            blocker = QSignalBlocker(oldWidget)
            oldWidget.deselect()

        self.currentPropIndex = index
        if -1 <= index < len(self.configuration):
            self.propertySelected.emit(self.configuration[index] if index >= 0 else None)

        if index >= 0: 
            newWidget: PropertyDisplay = self.main_layout.itemAt(index).widget() # type: ignore
            newWidget.select()

    def handlePropertySelected(self, selected: bool):
        selected_widget: PropertyDisplay = self.sender() # type: ignore
        selected_index = self.main_layout.indexOf(selected_widget)

        if self.inProgressIndex >= 0:
            if self.inProgressIndex == selected_index and not selected:
                selected_widget.select()
            elif self.inProgressIndex != selected_index and selected: 
                selected_widget.deselect()
        else:
            self.setCurrentPropertyIndex(selected_index if selected else -1) # type: ignore
        
    def addProperty(self, prop: Property):
        propDisplay = PropertyDisplay(self, prop)
        propDisplay.selected.connect(self.handlePropertySelected)
        self.main_layout.addWidget(propDisplay)
        propDisplay.select()
        self.setPredictionInProgress(self.main_layout.count() - 1)

    def removeProperty(self):
        item = self.main_layout.takeAt(self.currentPropIndex)
        item.widget().deleteLater() # type: ignore
        del item
        self.setPredictionInProgress(-1)
        self.setCurrentPropertyIndex(-1)
        