import os
import threading
import time
import requests
import util


class Uploader(threading.Thread):
    def __init__(self, config):
        super().__init__()
        self.config = config

    def run(self):
        while True:
            files = os.listdir(self.config["results_tmp_path"])
            for file in files:
                file_name, extension = file.split(".")
                hydrophone_id, timestamp, metric = file_name.split("_")
                year, month, day, hour, minute, second = timestamp.split("-")
                object_key = f"{self.config['operator_id']}/{hydrophone_id}/{metric}/{year}/{month}/{timestamp}.{extension}"
                presigned_response = util.get_presigned_upload_url(
                    self.config["presigned_upload_link_generator"],
                    self.config["bucket"],
                    object_key,
                )
                with open(f"{self.config['results_tmp_path']}/{file}", "rb") as f:
                    files = {"file": (f"{self.config['results_tmp_path']}/{file}", f)}
                    http_response = requests.post(
                        presigned_response["url"],
                        data=presigned_response["fields"],
                        files=files,
                    )
                if http_response.status_code != 204:
                    raise Exception(
                        f"Failed to upload file {file} to S3. Status code: {http_response.status_code}"
                    )
                os.remove(f"{self.config['results_tmp_path']}/{file}")
            time.sleep(self.config["upload_interval"])
