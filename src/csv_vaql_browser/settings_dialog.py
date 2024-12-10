from PySide6.QtCore import QMargins
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QCheckBox, QHBoxLayout, QLineEdit, QLabel, \
    QSpacerItem, QMessageBox

from csv_vaql_browser.tools.app_config import AppConfig
from csv_vaql_browser.tools.panel_widget import Panel


class SettingsDialog(QDialog):
    def __init__(self, parent, app_config: AppConfig):
        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.setModal(True)

        layout = QVBoxLayout()
        self.setLayout(layout)

        open_last_opened_file_on_load_cb = QCheckBox(
            "Automatically reopen last opened file when this application starts"
        )
        open_last_opened_file_on_load = app_config.get_value("open_last_opened_file_on_load", bool)
        if open_last_opened_file_on_load is None or not open_last_opened_file_on_load:
            open_last_opened_file_on_load_cb.setChecked(False)
        else:
            open_last_opened_file_on_load_cb.setChecked(True)
        layout.addWidget(open_last_opened_file_on_load_cb)

        # QComboBox()
        max_last_opened_files_le = QLineEdit()
        max_last_opened_files_le.setValidator(QIntValidator(bottom = 5, top = 30))
        max_last_opened_files = app_config.get_value("max_last_opened_files", int)
        max_last_opened_files = 10 if max_last_opened_files is None else max_last_opened_files
        max_last_opened_files_le.setText(f"{max_last_opened_files}")

        qh_box_layout = QHBoxLayout()
        qh_box_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.addWidget(Panel(
            qh_box_layout,
            [QLabel("Max number of last opened files"), max_last_opened_files_le, QSpacerItem]
        ))

        ok_button = QPushButton("Ok")

        def save_settings_and_close():
            try:
                max_last_opened_files = int(max_last_opened_files_le.text())
                app_config.set_value("max_last_opened_files", max_last_opened_files)
            except:
                QMessageBox.critical(parent, "Error", "Max number of last opened files is not a valid integer")
                return

            app_config.set_value("open_last_opened_file_on_load", open_last_opened_file_on_load_cb.isChecked())
            self.close()

        ok_button.clicked.connect(save_settings_and_close)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(lambda: self.close())
        layout.addWidget(Panel(QHBoxLayout(), [ok_button, cancel_button]))
