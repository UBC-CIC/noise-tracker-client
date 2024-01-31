import config
import re
from datetime import datetime


class DataFile:
    def __init__(self, file_path):
        self.file_path = f"{config.DIRECTORY_TO_WATCH}/{file_path}"
        self.timestamp = DataFile.parse_timestamp(file_path)

    @property
    def file_time_name(self):
        return self.timestamp.strftime("%Y_%m_%d_%H_%M_%S")

    @staticmethod
    def parse_timestamp(file_path):
        match = re.match(config.FILE_STRUCTURE_PATTERN, file_path)
        if not match:
            raise ValueError(
                f"File path {file_path} does not match the expected pattern"
            )

        year = match.group("year")
        month = match.group("month")
        day = match.group("day")
        hour = match.group("hour")
        minute = match.group("minute")
        second = match.group("second")

        return datetime(
            int(year), int(month), int(day), int(hour), int(minute), int(second)
        )
