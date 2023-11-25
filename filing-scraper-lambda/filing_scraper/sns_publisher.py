import boto3
import os
import logging

class SNSPublisher:
    def __init__(self) -> None:
        self.client = boto3.client("sns")
        self.snsArn = os.environ.get("SNS_ARN")

    def publish_email(self, subject: str, message: str):
        response = self.client.publish(TopicArn=self.snsArn,
                                       Message=message,
                                       Subject=subject)
        logging.info(f"Published with response {response}")