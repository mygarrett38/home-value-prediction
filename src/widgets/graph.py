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
    GraphMode.PREDICTION_RANGE: ((0, 1000), (0, 0)),
    GraphMode.ACREAGE_SQ_FT: ((0, 3), (0, 6000)),
    GraphMode.BED_BATH: ((0, 10), (0, 8))
}

Y_AXIS_NAMES = {
    GraphMode.PREDICTION_RANGE: ("", ""),
    GraphMode.ACREAGE_SQ_FT: ("Price (thousands of $)", "Price (thousands of $)"),
    GraphMode.BED_BATH: ("Price (thousands of $)", "Price (thousands of $)")
}

Y_AXIS_SCALES = {
    GraphMode.PREDICTION_RANGE: ((0, 10), (0, 0)),
    GraphMode.ACREAGE_SQ_FT: ((0, 1000), (0, 1000)),
    GraphMode.BED_BATH: ((0, 1000), (0, 1000))
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
        graphMode = self.configuration.graphMode

        x_lim = list(X_AXIS_SCALES[graphMode])
        y_lim = list(Y_AXIS_SCALES[graphMode])

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

                df_mmax = (max(df_m[X_AXIS_NAMES[graphMode][0]].max(), x_lim[0][1]), max(df_m[Y_AXIS_NAMES[graphMode][0]].max(), y_lim[0][1]))
                df_smax = (max(df_s[X_AXIS_NAMES[graphMode][1]].max(), x_lim[1][1]), max(df_s[Y_AXIS_NAMES[graphMode][1]].max(), y_lim[1][1]))
                df_moff = np.divide(df_mmax, 20.0)
                df_soff = np.divide(df_smax, 20.0)
                x_lim = ((0 - df_moff[0], df_mmax[0] + df_moff[0]), (0 - df_soff[0], df_smax[0] + df_soff[0]))
                y_lim = ((0 - df_moff[1], df_mmax[1] + df_moff[1]), (0 - df_soff[1], df_smax[1] + df_soff[1]))

                df_m.plot.scatter(x=X_AXIS_NAMES[graphMode][0], y=Y_AXIS_NAMES[graphMode][0], s=100, c="#ee0000", ax=self.axes_m)
                if currentProperty is not None: self.axes_m.plot(*propertyData(currentProperty, 0), marker="o", ms=15, zorder=2, color="#00ee00")
                df_s.plot.scatter(x=X_AXIS_NAMES[graphMode][1], y=Y_AXIS_NAMES[graphMode][1], s=100, c="#0000ee", ax=self.axes_s)
                if currentProperty is not None: self.axes_s.plot(*propertyData(currentProperty, 1), marker="o", ms=15, zorder=2, color="#00ee00")

            case GraphMode.PREDICTION_RANGE:
                df_m = pd.DataFrame([
                    propertyData(prop, 0) for prop in self.configuration
                ], columns=["Minimum", "Prediction", "Maximum"])
                df_m.insert(0, "Property", [prop.location.address for prop in self.configuration])

                x_max = max(df_m["Maximum"].max(), 1000)
                x_lim = ((x_max / -20.0, x_max * 1.05), (0, 0))
                y_lim = ((-0.5, len(self.configuration) - 0.5), (0, 0))

                df_m.apply(lambda row: self.axes_m.plot((row["Minimum"], row["Maximum"]), (row["Property"],) * 2, color="#888888", linewidth=4), axis=1)
                df_m.plot.scatter(x="Minimum",    y="Property", s=100, c="#eeaa00", zorder=3, ax=self.axes_m)
                df_m.plot.scatter(x="Prediction", y="Property", s=100, c="#00ee00", zorder=4, ax=self.axes_m)
                df_m.plot.scatter(x="Maximum",    y="Property", s=100, c="#eeaa00", zorder=3, ax=self.axes_m)

                if currentProperty is not None:
                    self.axes_m.plot(propertyData(currentProperty, 0)[::2], [currentProperty.location.address] * 2, zorder=2, color="#222222", linewidth=5)
                
                self.axes_m.set_xlabel(X_AXIS_NAMES[graphMode][0])
                self.axes_m.set_ylabel(Y_AXIS_NAMES[graphMode][0])

        self.axes_m.set_xlim(*x_lim[0])
        self.axes_m.set_ylim(*y_lim[0])
        self.axes_s.set_xlim(*x_lim[1])
        self.axes_s.set_ylim(*y_lim[1])

        self.figure.canvas.draw()