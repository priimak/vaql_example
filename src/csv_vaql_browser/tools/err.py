from typing import Callable

from PySide6.QtWidgets import QMessageBox, QWidget


def err[T](f: Callable[[], T]) -> T | Exception:
    try:
        return f()
    except Exception as ex:
        return ex


def msg_on_err(res: Exception | None, parent: QWidget) -> bool:
    if res is not None:
        QMessageBox.critical(parent, "Error", f"Error: {res}")
        return True
    else:
        return False
