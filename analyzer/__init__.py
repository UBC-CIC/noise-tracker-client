import json


def lambda_handler(event, context):
    # TODO implement
    return {
        "operator_id": "arshia",
        "hydrophones": [
            {
                "id": "337",
                "metrics": ["spectrogram"],
                "directory_to_watch": "/Users/arshia/repos/cic/noise-tracking/client/test",
                "file_structure_pattern": "^337_(?P<year>\\d{4})(?P<month>\\d{2})(?P<day>\\d{2})_(?P<hour>\\d{2})(?P<minute>\\d{2})(?P<second>\\d{2})_.*\\.wav$",
            },
            {
                "id": "410",
                "metrics": ["spectrogram"],
                "directory_to_watch": "/Users/arshia/repos/cic/noise-tracking/client/test",
                "file_structure_pattern": "^337_(?P<year>\\d{4})(?P<month>\\d{2})(?P<day>\\d{2})_(?P<hour>\\d{2})(?P<minute>\\d{2})(?P<second>\\d{2})_.*\\.wav$",
            },
        ],
        "scan_interval": 5,
        "upload_interval": 5,
        "bucket": "noise-tracker-hydrophones-data",
        "presigned_upload_link_generator": "https://glt2nqvvs9.execute-api.us-east-1.amazonaws.com/test/generate-presigned-upload-url",
        "processed_files_path": "./processed_files.txt",
        "results_tmp_path": "./results_tmp",
    }
