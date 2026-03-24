import numpy as np

from property import Property
from location import absolutePath

import joblib
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

import warnings
warnings.filterwarnings('ignore')

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
    
    def __iter__(self):
        return iter(self.properties)
    
    def __len__(self):
        return len(self.properties)
    
    def __contains__(self, prop: Property | None):
        return prop in self.properties
    
    def __getitem__(self, index: int):
        return self.properties[index]

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
        ames_prop = prop.toAmesModel()

        transform_type = self.ml_ames_ohe_type.transform([[ames_prop[0]]]).data  # type: ignore
        ames_prop[0] = float(transform_type[0]) if len(transform_type) > 0 else 1

        transform_heat = self.ml_ames_ohe_heat.transform([[ames_prop[4]]]).data  # type: ignore
        ames_prop[4] = float(transform_heat[0]) if len(transform_heat) > 0 else 1

        ames_prop = self.ml_ames_scaler.transform([ames_prop])
        price_ames = self.ml_ames_model.predict(ames_prop)

        loc_prop = prop.toLocationModel()
        loc_prop = self.ml_loc_scaler.transform([loc_prop])
        price_loc = self.ml_loc_model.predict(loc_prop)

        price_avg = np.mean((*price_ames, *price_loc))
        return float(np.expm1(price_avg))