from pathlib import Path
from typing import override, Callable

from PySide6.QtCore import QMargins
from PySide6.QtGui import QIcon, QCloseEvent
from PySide6.QtWidgets import QMessageBox, QMainWindow, QMenu, QWidget, QVBoxLayout

from csv_vaql_browser.app_context import AppContext
from csv_vaql_browser.menus import MainMenuBar
from csv_vaql_browser.panels import MainPanel, BottomPanel
from csv_vaql_browser.panels.vaql_input_panel import VAQLInputPanel
from csv_vaql_browser.tools.app_persist import AppPersistence


class MainWindow(QMainWindow):
    def __init__(self, screen_dim: tuple[int, int], app_persistence: AppPersistence):
        super().__init__()
        self.app_state = app_persistence.state
        self.app_config = app_persistence.config
        self.setWindowTitle("CSV Browser + VAQL")
        self.set_geometry(screen_dim[0], screen_dim[1])
        self.recently_opened_menu: QMenu | None = None

        cvsx_icon_file_path = Path(__file__).parent / "csv_browser.png"
        self.setWindowIcon(QIcon(f"{cvsx_icon_file_path}"))

        self.ctx = AppContext(app_persistence)

        # setup menu bar and panels
        main_menu_bar = MainMenuBar(self.ctx, dialogs_parent = self)
        self.setMenuBar(main_menu_bar)
        self.add_panels(
            top_panel = VAQLInputPanel(self, self.ctx),
            main_panel = MainPanel(self.ctx, main_menu_bar.file_menu.recently_opened_menu, dialogs_parent = self),
            bottom_panel = BottomPanel(self.ctx)
        )

        # connect dispatching methods in AppContext to relevant functions
        self.ctx.upd_last_opened_files_menu = self.update_last_opened_files_menu
        self.ctx.exit_application = self.close

        # re-open last opened file if so set in app config.
        if self.app_config.get_value("open_last_opened_file_on_load", bool | None) is True:
            last_opened_files = self.app_state.get_value("last_opened_files", [])
            if last_opened_files != []:
                self.ctx.load_csv_file(last_opened_files[0])

    @override
    def closeEvent(self, event: QCloseEvent):
        open_last_opened_file_on_load = self.app_config.get_value("open_last_opened_file_on_load", bool | None)
        if open_last_opened_file_on_load is None:
            # prompt user if he always wants to open last opened file
            result = QMessageBox.question(
                self, "Re-open file on start?",
                "Do you want to always automatically reopen last opened file when this application starts?"
            )
            self.app_config.set_value("open_last_opened_file_on_load", result == QMessageBox.StandardButton.Yes)

        self.app_state.save_geometry("main", self.saveGeometry())
        event.accept()

    def set_geometry(self, screen_width: int, screen_height: int):
        # Try loading geometry from saved app state
        loaded_geometry = self.app_state.get_geometry("main")
        if loaded_geometry is None:
            # Init main window size to be 60% of the screen size
            win_size_fraction = 0.6
            self.setGeometry(
                int(screen_width * (1 - win_size_fraction) / 2),
                int(screen_height * (1 - win_size_fraction) / 2),
                int(screen_width * win_size_fraction),
                int(screen_height * win_size_fraction)
            )
        else:
            self.restoreGeometry(loaded_geometry)

    def add_panels(self, *, top_panel: QWidget, main_panel: QWidget, bottom_panel: QWidget) -> None:
        root_panel = QWidget()
        layout = QVBoxLayout()
        root_panel.setLayout(layout)
        layout.setContentsMargins(QMargins(5, 5, 5, 1))
        layout.setSpacing(0)

        # top_panel.setStyleSheet("border: 3px solid red")
        layout.addWidget(top_panel)
        layout.addWidget(main_panel, stretch = 1)
        layout.addWidget(bottom_panel)

        self.setCentralWidget(root_panel)
        # self.centralWidget()

    def update_last_opened_files_menu(
            self,
            file_name: str,
            file_opener_factory: Callable[[str], Callable[[], None]]
    ) -> None:
        last_opened_files = self.app_state.get_value("last_opened_files", [])
        fname = f"{Path(file_name).absolute()}"

        # remove previously seen file as it will be placed at the top of this list
        last_opened_files = [f for f in last_opened_files if f != fname]

        # place it at the top
        last_opened_files.insert(0, fname)

        max_num_of_recorded_last_opened_files = self.app_config.get_value("max_last_opened_files", int)
        if len(last_opened_files) > max_num_of_recorded_last_opened_files:
            last_opened_files = last_opened_files[0:max_num_of_recorded_last_opened_files]
        self.app_state.save_value("last_opened_files", last_opened_files)

        self.update_prev_opened_submenu(file_opener_factory)  # update sub-menu "Prev Opened"

    def update_prev_opened_submenu(self, file_opener_factory: Callable[[str], Callable[[], None]]) -> None:
        if self.recently_opened_menu is not None:
            self.recently_opened_menu.clear()
            for file in self.app_state.get_value("last_opened_files", []):
                self.recently_opened_menu.addAction(file, file_opener_factory(file))
