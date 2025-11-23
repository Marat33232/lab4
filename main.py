import sys
import traceback
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(f"Критическая ошибка: {error_msg}")

    app = QApplication.instance()
    if app:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Ошибка")
        msg_box.setText("Произошла ошибка приложения")
        msg_box.setDetailedText(error_msg)
        msg_box.exec()


def main():
    sys.excepthook = handle_exception

    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    try:
        from main_window import MainWindow

        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Ошибка при запуске: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
