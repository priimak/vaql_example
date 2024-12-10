from PySide6.QtCore import QByteArray
from PySide6.QtWidgets import QWidget

from pyside6_by_example.tools import AppState


def set_geometry(
        widget: QWidget,
        app_state: AppState,
        screen_dim: tuple[int, int],
        win_size_fraction: float = 0.6
):
    # Try loading geometry from saved app state
    loaded_geometry: QByteArray | None = app_state.get_geometry(widget.objectName())
    if loaded_geometry is None:
        # Init main window size to be a fraction of the screen size
        widget.setGeometry(
            int(screen_dim[0] * (1 - win_size_fraction) / 2),
            int(screen_dim[1] * (1 - win_size_fraction) / 2),
            int(screen_dim[0] * win_size_fraction),
            int(screen_dim[1] * win_size_fraction)
        )
    else:
        widget.restoreGeometry(loaded_geometry)
