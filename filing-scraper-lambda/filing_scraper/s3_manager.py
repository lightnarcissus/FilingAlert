import logging
import os
from typing import List

import boto3
from botocore.exceptions import ClientError
import logging
logging.basicConfig(level=logging.INFO)

class S3Manager:
    _TMP_FOLDER = "tmp"
    def __init__(self) -> None:
        self.s3_client = boto3.client("s3")
        self.bucket_name = os.environ.get("S3_BUCKET_NAME", "filing-storage-ansh")

    def update_file(self, data: List[str], key: str, subfolder: str = "filing-scraper/"):
        local_file_path = self.get_current_file(key, subfolder=subfolder)
        with open(local_file_path, "w") as outfile:
            for entry in data:
                outfile.writelines([entry, "\n"])
        try:
            response = self.s3_client.upload_file(local_file_path, self.bucket_name, f"{subfolder}{key}")
        except ClientError as e:
            logging.error(e)

    def get_current_file(self, key: str, subfolder: str = "filing-scraper/") -> str:
        local_file_path = os.path.join(os.path.abspath(os.sep), self._TMP_FOLDER, key)
        logging.info(f"LOCAL FILE PATH {local_file_path}")
        # f = open(local_file_path, "x")
        # with open(local_file_path, 'w') as f:
        self.s3_client.download_file(self.bucket_name, f"{subfolder}{key}", local_file_path)
        return local_file_path
