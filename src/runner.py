import sys
import os.path
import json
from platformdirs import user_data_dir

from config import Configuration, absolutePath
from property import Property
from widgets.controller import Controller
from widgets.graph import GraphDisplay
from widgets.propertyDisplay import PropertyDisplayManager

from PySide6.QtCore import Qt, QObject, QThread, QTimer, Signal, Slot
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QIcon
from PySide6.QtUiTools import QUiLoader

import widgets.icons._icons

class HomeValueApplication(QApplication):
    processPrediction = Signal(Property)

    def __init__(self, argv: list[str]):
        super().__init__(argv)

        # Create the config directory if not exists
        os.makedirs(self.defaultConfigPath(), exist_ok=True)
        
        # Create the config file if not exists
        with open(self.defaultConfigFile(), "a"): pass

        # Load any existing data
        self.configuration = self.load()

        ui_loader = QUiLoader(self)
        ui_loader.registerCustomWidget(Controller)
        ui_loader.registerCustomWidget(GraphDisplay)
        ui_loader.registerCustomWidget(PropertyDisplayManager)
        window = ui_loader.load(absolutePath("widgets/home-value-window.ui"))

        self.controller = window.findChild(Controller, name="controller", options=Qt.FindChildOption.FindChildrenRecursively)
        if self.controller is None: raise ValueError("NEVER HAPPENS")

        self.controller.setMainWindow(window)
        self.controller.requestPrediction.connect(self.predictionRequested)
        self.processPrediction.connect(self.controller.predictionProcessed)

        window.showMaximized()
        window.destroyed.connect(self.save)
        window.destroyed.connect(self.quit)

    @Slot(Property)
    def predictionRequested(self, prop: Property):
        prop.price = self.configuration.predictProperty(prop)
        self.configuration.addProperty(prop)
        self.processPrediction.emit(prop)

    @classmethod
    def defaultConfigPath(cls):
        return user_data_dir("home-value-prediction", "su-cis-487")
    
    @classmethod
    def defaultConfigFile(cls, path: str | None = None):
        if path is None: path = cls.defaultConfigPath()
        return os.path.join(path, "config.json")
    
    def load(self, path: str | None = None):
        with open(self.defaultConfigFile(path)) as config_file:
            try: result = json.load(config_file, object_hook=Configuration.deserialize)
            except: result = Configuration()
        return result

    def save(self, path: str | None = None):
        if type(path) != str: path = None

        def serialize(config: Configuration): return config.serialize()

        with open(self.defaultConfigFile(path), "wt") as config_file:
            json.dump(self.configuration, config_file, default=serialize)

if __name__ == "__main__":
    sys.exit(HomeValueApplication(sys.argv).exec())