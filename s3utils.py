from typing import Final

from botocore.client import BaseClient

from setting import get_s3_config
import boto3
import os
from dotenv import load_dotenv

client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
)


def get_s3_client() -> BaseClient:
    return boto3.client("s3", aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("S3_SECRET_KEY"),)


def upload_s3_file(client: BaseClient, local_path: str, s3_path: str):
    client.upload_file(Filename=local_path, Bucket=BUCKET, Key=s3_path)


def download_s3_file(client: BaseClient, local_path: str, s3_path: str):
    client.download_file(Bucket=BUCKET, Key=s3_path, Filename=local_path)

