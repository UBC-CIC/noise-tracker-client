import sys
import os
import json
import requests
import threading
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QCheckBox,
    QGridLayout,
)

import constants
from analyzer.analyzer import Analyzer
from uploader.uploader import Uploader


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.analyzer_thread = None
        self.uploader_thread = None

        self.setWindowTitle("Configuration App")
        self.setGeometry(100, 100, 400, 200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.check_config()

    def closeEvent(self, event):
        if self.analyzer_thread:
            self.analyzer_thread.stop()
        if self.uploader_thread:
            self.uploader_thread.stop()
        event.accept()

    def check_config(self):
        if os.path.exists("config.json"):
            self.show_empty_ui()
        else:
            self.show_config_input()

    def show_empty_ui(self):
        layout = self.centralWidget().layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        label = QLabel("Configuration already exists.")
        layout.addWidget(label)

        with open("config.json", "r") as f:
            config = json.load(f)

        self.analyzer_thread = Analyzer(config)
        self.uploader_thread = Uploader(config)

        self.analyzer_thread.start()
        self.uploader_thread.start()

    def show_config_input(self):
        label = QLabel("Enter Operator ID:")
        self.centralWidget().layout().addWidget(label)

        self.user_id_input = QLineEdit()
        self.centralWidget().layout().addWidget(self.user_id_input)

        button = QPushButton("Get Configs")
        button.clicked.connect(self.get_configs)
        self.centralWidget().layout().addWidget(button)

    def get_configs(self):
        user_id = self.user_id_input.text()
        if not user_id:
            QMessageBox.warning(self, "Warning", "Please enter Operator ID.")
            return

        try:
            response = requests.get(constants.GET_OPERATOR_DETAILS_URL.format(user_id))
            response.raise_for_status()
            configs = response.json()
            dialog = QWidget()

            layout = QVBoxLayout(dialog)

            checkboxes = {}
            for hydrophone in configs["hydrophones"]:
                checkbox = QCheckBox(hydrophone["id"], dialog)
                layout.addWidget(checkbox)
                checkboxes[hydrophone["id"]] = checkbox

            button_box = QGridLayout()
            save_button = QPushButton("Save Selected")
            cancel_button = QPushButton("Cancel")
            button_box.addWidget(save_button, 0, 0)
            button_box.addWidget(cancel_button, 0, 1)
            layout.addLayout(button_box)

            save_button.clicked.connect(
                lambda: self.save_selected_configs(checkboxes, configs, dialog)
            )
            cancel_button.clicked.connect(lambda: dialog.close())

            dialog.setWindowTitle("Select Hydrophones to Monitor")
            dialog.setLayout(layout)
            dialog.show()

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(None, "Error", f"Failed to retrieve configs: {e}")

    def save_selected_configs(self, checkboxes, config, dialog):
        selected_hydrophones = [
            hydrophone_id
            for hydrophone_id, checkbox in checkboxes.items()
            if checkbox.isChecked()
        ]
        filtered_hydrophones = [
            hydrophone
            for hydrophone in config["hydrophones"]
            if hydrophone["id"] in selected_hydrophones
        ]
        filtered_configs = config.copy()
        filtered_configs["hydrophones"] = filtered_hydrophones

        try:
            with open("config.json", "w") as f:
                json.dump(filtered_configs, f)

            QMessageBox.information(
                None, "Success", "Selected configs retrieved and saved successfully."
            )
            self.show_empty_ui()
            dialog.close()

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to save configs: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
