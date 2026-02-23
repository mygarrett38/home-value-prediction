from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PySide6.QtWidgets import QWidget

import pandas as pd

class GraphDisplay(FigureCanvas):
    def __init__(self, parent: QWidget | None = None, w = 5, h = 4, dpi = 100):
        figure = Figure((w, h), dpi)
        self.axes = figure.add_subplot(111)
        self.axes.set_title("Test Graph")
        super().__init__(figure)

        df = pd.DataFrame([
           [0, 10], [3, 5], [2, 15], [10, 25], [4, 10],
        ], columns=['Test A', 'Test B'])

        # plot the pandas DataFrame, passing in the
        # matplotlib Canvas axes.
        df.plot(ax=self.axes)