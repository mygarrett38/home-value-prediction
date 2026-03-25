from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PySide6.QtWidgets import QWidget

from config import Configuration, GraphMode, TableMode
from property import Property

import numpy as np
import pandas as pd

TITLE_NAMES = {
    GraphMode.PREDICTION_RANGE: ("Model Prediction Ranges", ""),
    GraphMode.ACREAGE_SQ_FT: ("Price vs. Acreage", "Price vs. Square Footage"),
    GraphMode.BED_BATH: ("Price vs. Bedrooms", "Price vs. Bathrooms")
}

X_AXIS_NAMES = {
    GraphMode.PREDICTION_RANGE: ("Price (thousands of $)", ""),
    GraphMode.ACREAGE_SQ_FT: ("Acreage", "Interior Square Footage"),
    GraphMode.BED_BATH: ("Bedrooms", "Bathrooms")
}

X_AXIS_SCALES = {
    GraphMode.PREDICTION_RANGE: ((-50, 1050), (0, 0)),
    GraphMode.ACREAGE_SQ_FT: ((-0.1, 3.1), (-100, 6100)),
    GraphMode.BED_BATH: ((-0.5, 6.5), (-0.5, 5.5))
}

Y_AXIS_NAMES = {
    GraphMode.PREDICTION_RANGE: ("", ""),
    GraphMode.ACREAGE_SQ_FT: ("Price (thousands of $)", "Price (thousands of $)"),
    GraphMode.BED_BATH: ("Price (thousands of $)", "Price (thousands of $)")
}

Y_AXIS_SCALES = {
    GraphMode.PREDICTION_RANGE: ((-0.5, 10.5), (0, 0)),
    GraphMode.ACREAGE_SQ_FT: ((-50, 1050), (-50, 1050)),
    GraphMode.BED_BATH: ((-50, 1050), (-50, 1050))
}

class GraphDisplay(FigureCanvas):
    def __init__(self, parent: QWidget | None = None, w = 5, h = 4, dpi = 100):
        figure = Figure((w, h), dpi)
        super().__init__(figure)

        self.axes_m = figure.add_subplot(1, 2, 1)
        self.axes_s = figure.add_subplot(1, 2, 2)
    
    def setConfiguration(self, config: Configuration):
        self.configuration = config
        self.refresh(None)

    def refresh(self, currentProperty: Property | None):
        Y_AXIS_SCALES[GraphMode.PREDICTION_RANGE] = ((-0.5, len(self.configuration) - 0.5), (0, 0))
        graphMode = self.configuration.graphMode

        def propertyData(prop: Property, graph_num: int) -> tuple[float, float]:
            prop_data = {
                GraphMode.PREDICTION_RANGE: ((prop.price * 0.000835, prop.price / 1000, prop.price * 0.00118), ()),
                GraphMode.ACREAGE_SQ_FT: ((prop.acreage, prop.price / 1000), (prop.square_feet, prop.price / 1000)),
                GraphMode.BED_BATH: ((prop.beds, prop.price / 1000), (prop.totalBaths(), prop.price / 1000)),
            }

            return prop_data[graphMode][graph_num]

        self.axes_m.clear()
        self.axes_s.clear()
        self.axes_s.set_visible(graphMode != GraphMode.PREDICTION_RANGE)

        self.axes_m.set_position(pos=(0.1, 0.15, 0.35, 0.7) if graphMode != GraphMode.PREDICTION_RANGE else (0.2, 0.15, 0.7, 0.7))
        self.axes_s.set_position(pos=(0.6, 0.15, 0.35, 0.7))

        self.axes_m.set_title(TITLE_NAMES[graphMode][0])
        self.axes_s.set_title(TITLE_NAMES[graphMode][1])

        self.axes_m.set_xlim(*X_AXIS_SCALES[graphMode][0])
        self.axes_m.set_ylim(*Y_AXIS_SCALES[graphMode][0])
        self.axes_s.set_xlim(*X_AXIS_SCALES[graphMode][1])
        self.axes_s.set_ylim(*Y_AXIS_SCALES[graphMode][1])

        match graphMode:
            case GraphMode.ACREAGE_SQ_FT | GraphMode.BED_BATH:
                df_m = pd.DataFrame([
                    propertyData(prop, 0) for prop in self.configuration
                ], columns=[
                    group[graphMode][0] for group in [X_AXIS_NAMES, Y_AXIS_NAMES]
                ])
                df_s = pd.DataFrame([
                    propertyData(prop, 1) for prop in self.configuration
                ], columns=[
                    group[graphMode][1] for group in [X_AXIS_NAMES, Y_AXIS_NAMES]
                ])

                df_m.plot.scatter(x=X_AXIS_NAMES[graphMode][0], y=Y_AXIS_NAMES[graphMode][0], s=100, c="#ee0000", ax=self.axes_m)
                if currentProperty is not None: self.axes_m.plot(*propertyData(currentProperty, 0), marker="o", ms=15, zorder=2, color="#00ee00")
                df_s.plot.scatter(x=X_AXIS_NAMES[graphMode][1], y=Y_AXIS_NAMES[graphMode][1], s=100, c="#0000ee", ax=self.axes_s)
                if currentProperty is not None: self.axes_s.plot(*propertyData(currentProperty, 1), marker="o", ms=15, zorder=2, color="#00ee00")

            case GraphMode.PREDICTION_RANGE:
                df_m = pd.DataFrame([
                    propertyData(prop, 0) for prop in self.configuration
                ], columns=["Minimum", "Prediction", "Maximum"])
                df_m.insert(0, "Property", [prop.location.address for prop in self.configuration])

                df_m.apply(lambda row: self.axes_m.plot((row["Minimum"], row["Maximum"]), (row["Property"],) * 2, color="#888888", linewidth=4), axis=1)
                df_m.plot.scatter(x="Minimum",    y="Property", s=100, c="#eeaa00", zorder=3, ax=self.axes_m)
                df_m.plot.scatter(x="Prediction", y="Property", s=100, c="#00ee00", zorder=4, ax=self.axes_m)
                df_m.plot.scatter(x="Maximum",    y="Property", s=100, c="#eeaa00", zorder=3, ax=self.axes_m)

                if currentProperty is not None:
                    self.axes_m.plot(propertyData(currentProperty, 0)[::2], [currentProperty.location.address] * 2, zorder=2, color="#222222", linewidth=5)
                
                self.axes_m.set_xlabel(X_AXIS_NAMES[graphMode][0])
                self.axes_m.set_ylabel(Y_AXIS_NAMES[graphMode][0])

        self.figure.canvas.draw()