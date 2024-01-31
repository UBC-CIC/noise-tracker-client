import sys
import os
import threading
import time

import requests
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
)

import util
from analyzer.analyzer import Analyzer

import config
from data_file import DataFile


class S3UploaderApp(QWidget):
    def __init__(self, processed_files: set[str]):
        super().__init__()
        self.init_ui()
        self.s3_uploader = None
        self.processed_files = processed_files

    def init_ui(self):
        self.setWindowTitle("Noise Tracker")
        self.setGeometry(300, 300, 400, 200)

        self.folder_path_label = QLabel("Folder Path: ")

        self.select_folder_button = QPushButton("Run", self)
        self.select_folder_button.clicked.connect(self.run)

        layout = QVBoxLayout()
        layout.addWidget(self.select_folder_button)
        layout.addWidget(self.folder_path_label)

        self.setLayout(layout)

    def run(self):
        self.folder_path_label.setText(f"Folder Path: {config.DIRECTORY_TO_WATCH}")
        analyze_thread = threading.Thread(target=self.analyze_files, args=())
        upload_thread = threading.Thread(target=self.upload_results, args=())
        analyze_thread.start()
        upload_thread.start()

    def analyze_files(self):
        while True:
            current_files = util.find_files(
                config.DIRECTORY_TO_WATCH, config.FILE_STRUCTURE_PATTERN
            )
            new_files = current_files - self.processed_files
            for file in new_files:
                print(f"Detected new file: {file}")
                data_file = DataFile(file)
                Analyzer.analyze(data_file)
                with open(config.PROCESSED_FILES_PATH, "a") as f:
                    f.write(file + "\n")
                self.processed_files.add(file)
            time.sleep(config.SCAN_INTERVAL)

    def upload_results(self):
        while True:
            # upload file and delete after upload is done
            files = os.listdir(config.RESULTS_TMP_PATH)
            for file in files:
                object_key = (
                    f"{config.HYDROPHONE_OPERATOR_ID}/{config.HYDROPHONE_ID}/{file}"
                )
                presigned_response = util.get_presigned_upload_url(
                    config.BUCKET, object_key
                )
                with open(f"{config.RESULTS_TMP_PATH}/{file}", "rb") as f:
                    files = {"file": (f"{config.RESULTS_TMP_PATH}/{file}", f)}
                    http_response = requests.post(
                        presigned_response["url"],
                        data=presigned_response["fields"],
                        files=files,
                    )
                if http_response.status_code != 204:
                    raise Exception(
                        f"Failed to upload file {file} to S3. Status code: {http_response.status_code}"
                    )
                os.remove(f"{config.RESULTS_TMP_PATH}/{file}")
            time.sleep(config.UPLOAD_INTERVAL)


def main(processed_files: set[str]):
    app = QApplication(sys.argv)
    s3_uploader_app = S3UploaderApp(processed_files)
    s3_uploader_app.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    if not os.path.exists(config.RESULTS_TMP_PATH):
        os.makedirs(config.RESULTS_TMP_PATH)
    if not os.path.exists(config.PROCESSED_FILES_PATH):
        with open(config.PROCESSED_FILES_PATH, "w") as f:
            f.write("")
    processed_files: set[str] = set()
    with open(config.PROCESSED_FILES_PATH, "r") as f:
        for line in f:
            processed_files.add(line.strip())
    main(processed_files)
