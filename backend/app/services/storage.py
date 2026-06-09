import logging
import os
from pathlib import Path
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """
    Handles file storage operations.
    Connects to S3/MinIO if configuration parameters are provided.
    Falls back to local file storage for standalone development and offline testing.
    """

    def __init__(self):
        self.bucket_name = settings.S3_BUCKET_NAME
        self.use_s3 = bool(settings.S3_ACCESS_KEY and settings.S3_SECRET_KEY)
        self.s3_client = None

        if self.use_s3:
            try:
                # Initialize S3 Client
                client_kwargs = {
                    "aws_access_key_id": settings.S3_ACCESS_KEY,
                    "aws_secret_access_key": settings.S3_SECRET_KEY,
                    "region_name": settings.S3_REGION,
                    "config": Config(signature_version="s3v4")
                }
                # If endpoint URL is specified (e.g. MinIO), override standard AWS S3 endpoint
                if settings.S3_ENDPOINT_URL:
                    client_kwargs["endpoint_url"] = settings.S3_ENDPOINT_URL
                
                self.s3_client = boto3.client("s3", **client_kwargs)
                self.ensure_bucket_exists()
                logger.info(f"StorageService initialized successfully using S3 (bucket: {self.bucket_name})")
            except Exception as e:
                logger.error(f"Failed to initialize S3 storage. Falling back to local disk storage. Error: {str(e)}")
                self.use_s3 = False
        
        if not self.use_s3:
            # Set up local directory storage fallback
            self.local_base_path = Path("data/storage")
            self.local_base_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"StorageService initialized using local disk fallback at {self.local_base_path.resolve()}")

    def ensure_bucket_exists(self) -> None:
        """
        Creates the target S3 bucket if it does not already exist.
        """
        if not self.use_s3 or not self.s3_client:
            return
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "404":
                try:
                    logger.info(f"S3 bucket '{self.bucket_name}' not found. Creating bucket...")
                    # LocationConstraint is required for regions outside of us-east-1
                    if settings.S3_REGION == "us-east-1":
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={"LocationConstraint": settings.S3_REGION}
                        )
                    logger.info(f"S3 bucket '{self.bucket_name}' created successfully.")
                except Exception as ex:
                    logger.error(f"Failed to create S3 bucket: {str(ex)}")
                    raise ex
            else:
                logger.error(f"Error checking S3 bucket: {str(e)}")
                raise e

    def upload_file(self, file_content: bytes, destination_key: str) -> str:
        """
        Uploads document bytes to the active storage layer.
        Returns the key/path to retrieve the file.
        """
        if self.use_s3 and self.s3_client:
            try:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=destination_key,
                    Body=file_content
                )
                logger.debug(f"File uploaded successfully to S3: {destination_key}")
                return destination_key
            except Exception as e:
                logger.error(f"S3 upload failed for key '{destination_key}': {str(e)}")
                raise e
        else:
            try:
                # Save locally
                local_path = self.local_base_path / destination_key
                local_path.parent.mkdir(parents=True, exist_ok=True)
                with open(local_path, "wb") as f:
                    f.write(file_content)
                logger.debug(f"File uploaded successfully to local storage: {destination_key}")
                return destination_key
            except Exception as e:
                logger.error(f"Local storage upload failed for key '{destination_key}': {str(e)}")
                raise e

    def download_file(self, file_key: str) -> bytes:
        """
        Downloads and returns document bytes from the active storage layer.
        """
        if self.use_s3 and self.s3_client:
            try:
                response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
                return response["Body"].read()
            except Exception as e:
                logger.error(f"S3 download failed for key '{file_key}': {str(e)}")
                raise e
        else:
            try:
                local_path = self.local_base_path / file_key
                with open(local_path, "rb") as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Local storage download failed for key '{file_key}': {str(e)}")
                raise e

    def check_health(self) -> bool:
        """
        Verifies storage system status.
        """
        if self.use_s3 and self.s3_client:
            try:
                self.s3_client.head_bucket(Bucket=self.bucket_name)
                return True
            except Exception:
                return False
        else:
            return self.local_base_path.exists()


# Singleton storage service instance
storage_service = StorageService()
