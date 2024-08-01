import os
import re
import requests
import base64
import json


def find_files(directory, pattern):
    file_list = set()
    for root, dirs, files in os.walk(directory):
        for file in files:
            if re.match(pattern, file):
                file_list.add(file)
    return file_list


def get_presigned_upload_url(url, object_key):
    params = {"object_key": object_key}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(
            f"Failed to get presigned upload URL. Status code: {response.status_code}"
        )
    return json.loads(base64.b64decode(response.content))
