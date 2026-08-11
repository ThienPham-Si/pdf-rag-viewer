import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from app.config import settings
import logging

logger = logging.getLogger(__name__)

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT_URL,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1"
)

def upload_file_to_s3(file_obj, object_name: str) -> bool:
    """Upload a file-like object to an S3 bucket"""
    try:
        s3_client.upload_fileobj(file_obj, settings.S3_BUCKET, object_name)
        return True
    except ClientError as e:
        logger.error(f"S3 upload failed: {e}")
        return False
