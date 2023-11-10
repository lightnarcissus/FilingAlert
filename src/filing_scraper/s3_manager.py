import boto3
import logging
from botocore.exceptions import ClientError
import os
from typing import List

class S3Manager():
    def __init__(self) -> None:
        self.s3_client = boto3.client("s3")
        self.bucket_name = os.environ.get("S3_BUCKET_NAME", "apatel-projects")

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
        out_path = os.path.join(os.path.dirname(__file__), "tmp")
        os.makedirs(out_path, exist_ok=True)
        local_file_path = os.path.join(out_path, f"{key}")
        self.s3_client.download_file(self.bucket_name, f"{subfolder}{key}", local_file_path)
        return local_file_path
