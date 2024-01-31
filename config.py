# TODO: create interactive settings
HYDROPHONE_OPERATOR_ID = "arshia"
HYDROPHONE_ID = "337"
METRICS = ["spectrogram"]

SCAN_INTERVAL = 5  # scan every 5 seconds
UPLOAD_INTERVAL = 5  # upload every 60 seconds
DIRECTORY_TO_WATCH = "/Users/arshia/repos/cic/noise-tracking/client/test"
FILE_STRUCTURE_PATTERN = r"^337_(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})_(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})_.*\.wav$"
BUCKET = "noise-tracker-hydrophones-data"

PROCESSED_FILES_PATH = "./processed_files.txt"
RESULTS_TMP_PATH = "./results_tmp"


PRESIGNED_UPLOAD_LINK_GENERATOR = "https://glt2nqvvs9.execute-api.us-east-1.amazonaws.com/test/generate-presigned-upload-url"
