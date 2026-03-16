import os

from property import Property

from xgboost import XGBRegressor

def absolutePath(relative_path: str):
    return os.path.join(os.path.dirname(__file__), relative_path)

class Configuration:
    def __init__(self, **kwargs):
        # Load the machine learning models
        self.ml_ames_model = XGBRegressor()
        self.ml_ames_model.load_model(absolutePath("../model/xgb_ames.json"))

        self.ml_loc_model = XGBRegressor()
        self.ml_loc_model.load_model(absolutePath("../model/xgb_loc.json"))

        # Init the properties list
        self.properties: list[Property] = kwargs["properties"]

    @staticmethod
    def deserialize(obj: dict):
        if "version" in obj:
            return Configuration(**obj)
        
        return Property.deserialize(obj)
    
    def serialize(self):
        return {
            "version": [0, 1, 0],
            "properties": [prop.serialize() for prop in self.properties]
        }