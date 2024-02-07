import re
from datetime import datetime


class DataFile:
    def __init__(self, file_path: str, hydrophone: dict):
        self.file_path: str = file_path
        self.timestamp: datetime = self.parse_timestamp(file_path, hydrophone)
        self.hydrophone: dict = hydrophone

    def file_time_name(self):
        return f"{self.hydrophone['id']}_{self.timestamp.strftime('%Y/%m/%d-%H-%M-%S')}"

    @staticmethod
    def parse_timestamp(file_path, hydrophone):
        file_name = file_path.split("/")[-1]
        match = re.match(hydrophone["file_structure_pattern"], file_name)
        if not match:
            raise ValueError(
                f"File path {file_path} does not match the expected pattern {hydrophone['file_structure_pattern']}"
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
