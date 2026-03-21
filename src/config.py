import os

import numpy as np

from property import Property

import joblib
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

def absolutePath(relative_path: str):
    return os.path.join(os.path.dirname(__file__), relative_path)

class Configuration:
    def __init__(self, **kwargs):
        # Load the machine learning models
        self.ml_ames_model = XGBRegressor()
        self.ml_ames_model.load_model(absolutePath("../model/xgb_ames.json"))

        self.ml_ames_ohe_type: OneHotEncoder = joblib.load(absolutePath("../model/ohe_ames_BldgType.joblib"))
        self.ml_ames_ohe_heat: OneHotEncoder = joblib.load(absolutePath("../model/ohe_ames_Heating.joblib"))
        self.ml_ames_scaler: StandardScaler = joblib.load(absolutePath("../model/scl_ames.joblib"))

        self.ml_loc_model = XGBRegressor()
        self.ml_loc_model.load_model(absolutePath("../model/xgb_loc.json"))

        self.ml_loc_scaler: StandardScaler = joblib.load(absolutePath("../model/scl_loc.joblib"))

        # Init the properties list
        self.properties: list[Property] = kwargs["properties"] if len(kwargs) > 0 else []

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
    
    def addProperty(self, prop: Property):
        self.properties.append(prop)

    def setProperty(self, index: int, prop: Property):
        self.properties.insert(index, prop)

    def removeProperty(self, index: int):
        self.properties.pop(index)

    def predictProperty(self, prop: Property):
        price_ames = self.ml_ames_model.predict([prop.toAmesModel()])
        price_loc = self.ml_loc_model.predict([prop.toLocationModel()])
        price_norm = np.expm1((*price_ames, *price_loc))
        print(price_norm)

        return float(sum(price_norm)) / 2.0