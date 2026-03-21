from PySide6.QtCore import (
    Qt,
    Signal
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


class PropertyDisplay(QWidget):
    selected = Signal()

    def __init__(self, parent: QWidget, property: Property):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.prop = property
        self.setObjectName(str(id(property)))
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        self.setLayout(main_layout)

        """ self.selectedWidget = QCheckBox("", parent=self)
        main_layout.addWidget(self.selectedWidget) """

        desc_layout = QVBoxLayout()
        desc_layout.setContentsMargins(0, 0, 0, 0)
        desc_layout.setSpacing(5)
        main_layout.addLayout(desc_layout, stretch=1)

        propFont = self.font()
        propFont.setPointSize(14)
        propFont.setBold(True)

        self.addressLabel = QLabel(property.location_address, parent=self)
        self.addressLabel.setFont(propFont)
        desc_layout.addWidget(self.addressLabel)

        propFont.setPointSize(11)
        propFont.setBold(False)

        self.propertyLabel = QLabel("", parent=self)
        self.propertyLabel.setFont(propFont)
        self.refreshPropertyAttributes()
        desc_layout.addWidget(self.propertyLabel)

        propFont.setPointSize(12)
        propFont.setItalic(True)

        self.priceLabel = QLabel(f"${round(property.price / 1000)}k", parent=self, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.priceLabel.setFont(propFont)
        main_layout.addWidget(self.priceLabel)

    def select(self):
        self.setProperty("selected", 1)
        resetStylesheet(self)
        self.selected.emit()

    def deselect(self):
        self.setProperty("selected", 0)
        resetStylesheet(self)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        self.select()
        return super().mouseDoubleClickEvent(event)

    def refreshPropertyAttributes(self):
        attrs = self.prop.attributes()
        self.propertyLabel.setText(" | ".join(attrs))


class PropertyDisplayManager(QWidget):
    propertySelected = Signal(Property)
    propertyEditRequested = Signal(Property)
    propertyRemoveRequested = Signal(Property)

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

        self.currentProp = None

    def setConfiguration(self, config: Configuration):
        self.configuration = config

    def connectButton(self, button: QPushButton, /, type: str):
        buttons = {
            "add": self.addProperty,
            "edit": self.editProperty,
            "remove": self.removeProperty
        }
        if type not in buttons.keys(): raise ValueError("Incorrect button connection type!")

        button.clicked.connect(buttons[type])

    def setCurrentProperty(self, prop: Property):
        pass

    def currentProperty(self):
        return self.currentProp

    def addProperty(self):
        self.currentProp = Property()
        propDisplay = PropertyDisplay(self, self.currentProp)
        self.main_layout.addWidget(propDisplay)
        propDisplay.select()

        self.propertyEditRequested.emit(self.currentProp)

    def editProperty(self):
        self.propertyEditRequested.emit(self.currentProp)

    def removeProperty(self):
        #removingDisplay = self.main_layout.findChild(PropertyDisplay, str(id(self.currentProp)))
        #if removingDisplay is None: raise ValueError("removeProperty(): No property display found!")
        if QMessageBox.question(self, "Are you sure?", "This property and its prediction will be permanently deleted.\n\nAre you sure you want to do this?") == QMessageBox.StandardButton.Cancel: return

        #self.configuration.removeProperty(self.)
        #self.main_layout.removeWidget(removingDisplay)