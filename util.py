import os
import re
import requests
import config


def find_files(directory, pattern):
    file_list = set()
    for root, dirs, files in os.walk(directory):
        for file in files:
            if re.match(pattern, file):
                file_list.add(file)
    return file_list


def get_presigned_upload_url(bucket_name, object_key):
    data = {"bucket_name": bucket_name, "object_key": object_key}
    response = requests.get(config.PRESIGNED_UPLOAD_LINK_GENERATOR, json=data).json()
    return response["body"]
