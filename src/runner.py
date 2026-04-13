import sys
import os.path
import json
from platformdirs import user_data_dir

from config import Configuration
from property import Property
from location import Location, resourcePath
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
    processLocation = Signal()

    def __init__(self, argv: list[str]):
        super().__init__(argv)

        # Load Location service
        self.location_client = Location.load()
        self.lastLocation = None

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
        window = ui_loader.load(resourcePath("src/widgets/home-value-window.ui"))

        self.controller = window.findChild(Controller, name="controller", options=Qt.FindChildOption.FindChildrenRecursively)
        if self.controller is None: raise ValueError("NEVER HAPPENS")

        self.controller.setConfiguration(self.configuration)
        self.controller.setMainWindow(window)
        self.controller.requestPrediction.connect(self.predictionRequested)
        self.processPrediction.connect(self.controller.predictionProcessed)
        self.controller.requestLocation.connect(self.locationRequested)
        self.processLocation.connect(self.controller.locationProcessed)

        window.showMaximized()
        window.destroyed.connect(self.save)
        window.destroyed.connect(self.quit)

    @Slot(Property)
    def predictionRequested(self, prop: Property):
        prop.price = self.configuration.predictProperty(prop)
        if prop not in self.configuration: self.configuration.addProperty(prop)
        self.processPrediction.emit(prop)

    @Slot(Property)
    def locationRequested(self, prop: Property):
        if prop.location != self.lastLocation:
            self.lastLocation = prop.location
            prop.location.requestLocation(self.location_client)
        self.processLocation.emit()

    @classmethod
    def defaultConfigPath(cls):
        return user_data_dir("home-value-prediction", "su-cis-487")
    
    @classmethod
    def defaultConfigFile(cls, path: str | None = None):
        if path is None: path = cls.defaultConfigPath()
        return os.path.join(path, "config.json")
    
    @classmethod
    def deserialize(cls, obj: dict):
        if "version" in obj:
            return Configuration(**obj)
        elif "coordinates" in obj:
            return Location(**obj)
        else:
            return Property(**obj)
    
    def load(self, path: str | None = None):
        with open(self.defaultConfigFile(path)) as config_file:
            try: result = json.load(config_file, object_hook=self.deserialize)
            except Exception as error:
                #print(error)
                result = Configuration()
        return result

    def save(self, path: str | None = None):
        if type(path) != str: path = None

        def serialize(config: Configuration): return config.serialize()

        with open(self.defaultConfigFile(path), "wt") as config_file:
            json.dump(self.configuration, config_file, default=serialize)

if __name__ == "__main__":
    sys.exit(HomeValueApplication(sys.argv).exec())