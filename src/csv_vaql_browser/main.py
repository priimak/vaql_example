import sys

from PySide6.QtWidgets import QApplication

from csv_vaql_browser.main_window import MainWindow
from csv_vaql_browser.tools.app_persist import AppPersistence


def main():
    app = QApplication(sys.argv)

    # Will init main window size to be some fraction of the screen size
    # unless defined elsewhere
    screen_width, screen_height = app.primaryScreen().size().toTuple()

    persistence = AppPersistence(
        app_name = "vaql_csv_browser",
        init_config_data = {
            "max_last_opened_files": 10,
            "open_last_opened_file_on_load": None
        }
    )
    win = MainWindow(screen_dim = (screen_width, screen_height), app_persistence = persistence)
    win.show()
    win.reopen_last_opened_file.emit()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
