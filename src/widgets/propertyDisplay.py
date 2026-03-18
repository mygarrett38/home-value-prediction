from PySide6.QtCore import (
    Qt,
    Signal
)

from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QWidget,
    QSizePolicy,
    QHBoxLayout,
    QVBoxLayout,
    QCheckBox,
    QLabel,
)

def resetStylesheet(widget: QWidget):
    ss = widget.styleSheet()
    widget.setStyleSheet("/* */")
    widget.setStyleSheet(ss)


class PropertyDisplay(QWidget):
    selected = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
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

        self.addressLabel = QLabel("", parent=self)
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

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        self.selected.emit()
        self.setProperty("selected", 1)
        resetStylesheet(self)
        return super().mouseDoubleClickEvent(event)

    def setAddress(self, address: str):
        self.addressLabel.setText(address)

    def setPropertyAttributes(self, attrs: list[str]):
        self.propertyLabel.setText(" | ".join(attrs))

    def setPrice(self, price: int):
        self.priceLabel.setText(f"${price:,.2f}")
