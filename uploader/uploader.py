import os
import threading
import time
import requests

import constants
import util
from logger import logger


class Uploader(threading.Thread):
    def __init__(self, config):
        super().__init__()
        self.__stop_event = threading.Event()
        self.config = config

    def stop(self):
        self.__stop_event.set()

    def stopped(self):
        return self.__stop_event.is_set()

    def run(self):
        while True and not self.stopped():
            files = os.listdir(constants.RESULTS_TMP_PATH)
            for file in files:
                logger.info(f"Uploading file {file} to S3")
                file_name, extension = file.split(".")
                hydrophone_id, timestamp, metric = file_name.split("_")
                year, month, day, hour, minute, second = timestamp.split("-")
                object_key = f"{self.config['operator_id']}/{hydrophone_id}/{metric}/{year}/{month}/{timestamp}.{extension}"
                try:
                    presigned_response = util.get_presigned_upload_url(
                        constants.PRESIGNED_UPLOAD_LINK_GENERATOR,
                        object_key,
                    )
                except Exception as e:
                    logger.error(f"Failed to get presigned upload URL: {e}")
                    time.sleep(self.config["upload_interval"])
                    continue
                with open(f"{constants.RESULTS_TMP_PATH}/{file}", "rb") as f:
                    files = {"file": (f"{constants.RESULTS_TMP_PATH}/{file}", f)}
                    http_response = requests.post(
                        presigned_response["url"],
                        data=presigned_response["fields"],
                        files=files,
                    )
                if http_response.status_code != 204:
                    logger.error(
                        f"Failed to upload file {file} to S3. Status code: {http_response.status_code}"
                    )
                else:
                    logger.info(f"Uploaded file {file} to S3")
                os.remove(f"{constants.RESULTS_TMP_PATH}/{file}")
            time.sleep(self.config["upload_interval"])
