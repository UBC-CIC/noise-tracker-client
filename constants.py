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

PROCESSED_FILES_PATH = os.path.join(BASE_PATH, "processed_files.txt")
RESULTS_TMP_PATH = os.path.join(BASE_PATH, "results_tmp")
CONFIG_PATH = os.path.join(BASE_PATH, "config.json")


# Fill in the following constants with the appropriate values
BUCKET = ""  # name of the bucket
PRESIGNED_UPLOAD_LINK_GENERATOR = ""  # url to the upload link generator lambda function
GET_OPERATOR_DETAILS_URL = (
    "" + "?operator_id={}"
)  # url for operator configuration lambda function
