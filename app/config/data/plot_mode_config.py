from enum import Enum


class PlotMode(Enum):
    SCATTER = "scatter"
    BAR = "bar"
    LINE = "line"
    HEATMAP = "heatmap"

    @staticmethod
    def list_modes():
        """Return list of available plot modes"""
        return [mode.value for mode in PlotMode]
