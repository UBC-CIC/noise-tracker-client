import os
import platform

BASE_PATH = ""
if platform.system() == "Darwin":
    BASE_PATH = os.path.join(
        os.path.expanduser("~"), "Library", "Application Support", "NoiseTracker"
    )
elif platform.system() == "Windows":
    BASE_PATH = os.path.join(os.getenv("APPDATA"), "NoiseTracker")
elif platform.system() == "Linux":
    BASE_PATH = os.path.join(os.path.expanduser("~"), ".NoiseTracker")
else:
    raise Exception("Unsupported OS")

BUCKET = "noise-tracker-hydrophones-data"
PRESIGNED_UPLOAD_LINK_GENERATOR = "https://glt2nqvvs9.execute-api.us-east-1.amazonaws.com/test/generate-presigned-upload-url"
PROCESSED_FILES_PATH = os.path.join(BASE_PATH, "processed_files.txt")
RESULTS_TMP_PATH = os.path.join(BASE_PATH, "results_tmp")
CONFIG_PATH = os.path.join(BASE_PATH, "config.json")
GET_OPERATOR_DETAILS_URL = "https://glt2nqvvs9.execute-api.us-east-1.amazonaws.com/test/get-operator-config?operator_id={}"
