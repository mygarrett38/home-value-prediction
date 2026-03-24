from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PySide6.QtWidgets import QWidget

from config import Configuration, GraphMode, TableMode

import pandas as pd

class GraphDisplay(FigureCanvas):
    def __init__(self, parent: QWidget | None = None, w = 5, h = 4, dpi = 100):
        figure = Figure((w, h), dpi)
        figure.subplots_adjust(0.1, 0.15, 0.95, 0.85, 0.3, 0.1)
        super().__init__(figure)

        self.axes_m = figure.add_subplot(1, 2, 1)
        self.axes_m.set_title("Price vs. Acreage")

        self.axes_s = figure.add_subplot(1, 2, 2)
        self.axes_s.set_title("Price vs. Square Footage")

        self.axes_m.set_xlim(0, 2)
        self.axes_m.set_ylim(0, 1000)
        self.axes_s.set_xlim(0, 5000)
        self.axes_s.set_ylim(0, 1000)

        dfa = pd.DataFrame([
            [0.45, 525000.0],
            [0.36, 289900.0],
            [0.11, 275000.0],
            [0.24, 335000.0],
            [0.46, 384900.0],
            [1.63, 779900.0],
            [1.76, 199999.0]
        ], columns=['Acreage', 'Price (thousands)'])
        dfa["Price (thousands)"] /= 1000
        dfb = pd.DataFrame([
            [2314.0, 525000.0],
            [1276.0, 289900.0],
            [1732.0, 275000.0],
            [1800.0, 335000.0],
            [1476.0, 384900.0],
            [2910.0, 779900.0],
            [1968.0, 199999.0]
        ], columns=['Interior Square Footage', 'Price (thousands)'])
        dfb["Price (thousands)"] /= 1000

        dfa.plot.scatter(x="Acreage", y="Price (thousands)", s=50, c="#ee0000", ax=self.axes_m)
        dfb.plot.scatter(x="Interior Square Footage", y="Price (thousands)", s=50, c="#0000ee", ax=self.axes_s)
    
    def setConfiguration(self, config: Configuration):
        self.configuration = config

    def refresh(self):
        graphMode = self.configuration.graphMode

        #self.axes_m.clear()
        #self.axes_s.clear()
        self.axes_s.set_visible(graphMode != GraphMode.PREDICTION_RANGE)

        self.figure.canvas.draw()