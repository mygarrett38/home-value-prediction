from PySide6.QtCore import (
    Qt
)

from PySide6.QtWidgets import (
    QWidget,
    QSizePolicy,
    QHBoxLayout,
    QVBoxLayout,
    QCheckBox,
    QLabel,
)


class HistoryEntry(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        self.setLayout(main_layout)

        self.selectedWidget = QCheckBox("", parent=self)
        main_layout.addWidget(self.selectedWidget)

        desc_layout = QVBoxLayout()
        desc_layout.setContentsMargins(0, 0, 0, 0)
        desc_layout.setSpacing(5)
        main_layout.addLayout(desc_layout, stretch=1)

        propFont = self.font()
        propFont.setPointSize(16)
        propFont.setBold(True)

        self.addressLabel = QLabel("", parent=self)
        self.addressLabel.setFont(propFont)
        desc_layout.addWidget(self.addressLabel)

        propFont.setPointSize(14)
        propFont.setBold(False)

        self.propertyLabel = QLabel("", parent=self)
        self.propertyLabel.setFont(propFont)
        desc_layout.addWidget(self.propertyLabel)

    def setAddress(self, address: str):
        self.addressLabel.setText(address)

    def setPropertyAttributes(self, attrs: list[str]):
        self.propertyLabel.setText(" | ".join(attrs))
