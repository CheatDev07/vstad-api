# from datetime import timedelta
# from minio import Minio
# from minio.error import S3Error
# from config import settings
# import os
# from io import BytesIO
# import json

# class MinIOClient:
#     def __init__(self):
#         # Internal endpoint for server-to-server communication
#         self.internal_endpoint = settings.MINIO_ENDPOINT
        
#         # External endpoint for client-facing URLs
#         self.external_endpoint = settings.MINIO_EXTERNAL_ENDPOINT
        
#         # Client for internal operations (upload, delete, etc.)
#         self.client = Minio(
#             self.internal_endpoint,
#             access_key=settings.MINIO_ACCESS_KEY,
#             secret_key=settings.MINIO_SECRET_KEY,
#             secure=False
#         )
        
#         # Client for generating public URLs with correct signatures
#         self.public_client = Minio(
#             self.external_endpoint,
#             access_key=settings.MINIO_ACCESS_KEY,
#             secret_key=settings.MINIO_SECRET_KEY,
#             secure=False
#         )
        
#         self.bucket_name = settings.MINIO_BUCKET_NAME
#         self._ensure_bucket_exists()
#         self._configure_bucket_policy()
        
    
#     def _ensure_bucket_exists(self):
#         """Create bucket if it doesn't exist"""
#         try:
#             if not self.client.bucket_exists(self.bucket_name):
#                 self.client.make_bucket(self.bucket_name)
#                 print(f"Bucket '{self.bucket_name}' created successfully")
#         except S3Error as e:
#             print(f"Error creating bucket: {e}")
    
#     def _configure_bucket_policy(self):
#         """Configure bucket policy to allow public read access"""
#         try:
#             policy = {
#                 "Version": "2012-10-17",
#                 "Statement": [
#                     {
#                         "Effect": "Allow",
#                         "Principal": {"AWS": ["*"]},
#                         "Action": ["s3:GetObject"],
#                         "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"]
#                     }
#                 ]
#             }
            
#             policy_json = json.dumps(policy)
#             print(f"Setting policy: {policy_json}")
            
#             self.client.set_bucket_policy(self.bucket_name, policy_json)
            
#             # Verify it was set
#             current_policy = self.client.get_bucket_policy(self.bucket_name)
#             print(f"✓ Bucket '{self.bucket_name}' is now PUBLIC")
#             print(f"✓ Current policy: {current_policy}")
            
#         except S3Error as e:
#             print(f"✗ Error setting bucket policy: {e}")
#             print(f"✗ Error details: {e.message if hasattr(e, 'message') else str(e)}")
    
#     def upload_file(self, file_path: str, object_name: str) -> bool:
#         """Upload file to MinIO"""
#         try:
#             self.client.fput_object(
#                 self.bucket_name,
#                 object_name,
#                 file_path,
#                 content_type="video/mp4"
#             )
#             print(f"File '{object_name}' uploaded successfully")
#             return True
#         except S3Error as e:
#             print(f"Error uploading file: {e}")
#             return False
    
#     def upload_fileobj(self, file_bytes: BytesIO, object_name: str, file_size: int, content_type: str = "video/mp4") -> bool:
#         """Upload file from bytes"""
#         try:
#             file_bytes.seek(0)
#             self.client.put_object(
#                 self.bucket_name,
#                 object_name,
#                 file_bytes,
#                 file_size,
#                 content_type=content_type
#             )
#             print(f"File '{object_name}' uploaded successfully from bytes")
#             return True
#         except S3Error as e:
#             print(f"Error uploading file: {e}")
#             return False
    
#     def download_file(self, object_name: str, file_path: str) -> bool:
#         """Download file from MinIO"""
#         try:
#             self.client.fget_object(self.bucket_name, object_name, file_path)
#             print(f"File '{object_name}' downloaded successfully")
#             return True
#         except S3Error as e:
#             print(f"Error downloading file: {e}")
#             return False
    
#     def download_fileobj(self, object_name: str) -> BytesIO:
#         """Download file as bytes"""
#         try:
#             response = self.client.get_object(self.bucket_name, object_name)
#             file_bytes = BytesIO(response.read())
#             response.close()
#             response.release_conn()
#             return file_bytes
#         except S3Error as e:
#             print(f"Error downloading file: {e}")
#             return None
    
#     def delete_file(self, object_name: str) -> bool:
#         """Delete file from MinIO"""
#         try:
#             self.client.remove_object(self.bucket_name, object_name)
#             print(f"File '{object_name}' deleted successfully")
#             return True
#         except S3Error as e:
#             print(f"Error deleting file: {e}")
#             return False
    
#     def list_objects(self, prefix: str = "") -> list:
#         """List objects in bucket"""
#         try:
#             objects = self.client.list_objects(self.bucket_name, prefix=prefix)
#             return [obj.object_name for obj in objects]
#         except S3Error as e:
#             print(f"Error listing objects: {e}")
#             return []

#     def get_object_url(self, object_name: str) -> str:
#         """Get public URL for object (direct access, no signature)"""
#         # Direct URL for public bucket
#         return f"http://{self.external_endpoint}/{self.bucket_name}/{object_name}"
    
#     def get_object_url_download(self, object_name: str, expiration: int = 3600) -> str:
#         """Get presigned URL for object download using external endpoint"""
#         try:
#             # Use public_client to generate URL with correct external endpoint
#             url = self.public_client.presigned_get_object(
#                 self.bucket_name,
#                 object_name,
#                 expires=timedelta(seconds=expiration)
#             )
#             return url
#         except S3Error as e:
#             print(f"Error getting object URL: {e}")
#             return None
    
#     def get_object_url_upload(self, object_name: str, expiration: int = 3600) -> str:
#         """Get presigned URL for object upload using external endpoint"""
#         try:
#             # Use public_client to generate upload URL with correct external endpoint
#             url = self.public_client.presigned_put_object(
#                 self.bucket_name,
#                 object_name,
#                 expires=timedelta(seconds=expiration)
#             )
#             return url
#         except S3Error as e:
#             print(f"Error getting upload URL: {e}")
#             return None


# # Global MinIO client instance
# minio_client = MinIOClient()




import json
from minio import Minio
from minio.error import S3Error
from config import settings
import os
from io import BytesIO
from datetime import timedelta
import time
from functools import wraps

def retry_on_connection_error(max_retries=3, delay=2):
    """Decorator to retry on connection errors"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"[Retry {attempt + 1}/{max_retries}] Error in {func.__name__}: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        raise
            return None
        return wrapper
    return decorator

class MinIOClient:
    def __init__(self):
        # Internal client for server-to-server communication within Docker
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )
        
        # External client for generating presigned URLs for client-facing access
        self.external_client = Minio(
            settings.MINIO_EXTERNAL_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )
        
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self.profile_bucket_name = "videos"
        self._ensure_buckets_exist()
        self._configure_bucket_policy()


    def _configure_bucket_policy(self):
        """Configure bucket policy to allow public read access"""
        try:
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"]
                    }
                ]
            }
            
            policy_json = json.dumps(policy)
            print(f"Setting policy: {policy_json}")
            
            self.client.set_bucket_policy(self.bucket_name, policy_json)
            
            # Verify it was set
            current_policy = self.client.get_bucket_policy(self.bucket_name)
            print(f"✓ Bucket '{self.bucket_name}' is now PUBLIC")
            print(f"✓ Current policy: {current_policy}")
            
        except S3Error as e:
            print(f"✗ Error setting bucket policy: {e}")
            print(f"✗ Error details: {e.message if hasattr(e, 'message') else str(e)}")

    @retry_on_connection_error(max_retries=3, delay=2)
    def _ensure_buckets_exist(self):
        """Create buckets if they don't exist"""
        try:
            # Create videos bucket
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                print(f"Bucket '{self.bucket_name}' created successfully")
            
            # Create profiles bucket
            if not self.client.bucket_exists(self.profile_bucket_name):
                self.client.make_bucket(self.profile_bucket_name)
                print(f"Bucket '{self.profile_bucket_name}' created successfully")
        except S3Error as e:
            print(f"Error creating buckets: {e}")
            raise
    
    @retry_on_connection_error(max_retries=3, delay=2)
    def upload_file(self, file_path: str, object_name: str, bucket: str = None, content_type: str = "video/mp4") -> bool:
        """Upload file to MinIO"""
        try:
            bucket = bucket or self.bucket_name
            file_size = os.path.getsize(file_path)
            self.client.fput_object(
                bucket,
                object_name,
                file_path,
                content_type=content_type
            )
            print(f"File '{object_name}' uploaded successfully to '{bucket}'")
            return True
        except S3Error as e:
            print(f"Error uploading file: {e}")
            return False
    
    @retry_on_connection_error(max_retries=3, delay=2)
    def upload_fileobj(self, file_bytes: BytesIO, object_name: str, file_size: int, bucket: str = None, content_type: str = "video/mp4") -> bool:
        """Upload file from bytes"""
        try:
            bucket = bucket or self.bucket_name
            file_bytes.seek(0)
            self.client.put_object(
                bucket,
                object_name,
                file_bytes,
                file_size,
                content_type=content_type
            )
            print(f"File '{object_name}' uploaded successfully from bytes to '{bucket}'")
            return True
        except S3Error as e:
            print(f"Error uploading file: {e}")
            return False
    
    @retry_on_connection_error(max_retries=3, delay=2)
    def download_file(self, object_name: str, file_path: str, bucket: str = None) -> bool:
        """Download file from MinIO"""
        try:
            bucket = bucket or self.bucket_name
            self.client.fget_object(bucket, object_name, file_path)
            print(f"File '{object_name}' downloaded successfully from '{bucket}'")
            return True
        except S3Error as e:
            print(f"Error downloading file: {e}")
            return False
    
    @retry_on_connection_error(max_retries=3, delay=2)
    def download_fileobj(self, object_name: str, bucket: str = None) -> BytesIO:
        """Download file as bytes"""
        try:
            bucket = bucket or self.bucket_name
            response = self.client.get_object(bucket, object_name)
            file_bytes = BytesIO(response.read())
            response.close()
            response.release_conn()
            return file_bytes
        except S3Error as e:
            print(f"Error downloading file: {e}")
            return None
    
    @retry_on_connection_error(max_retries=3, delay=2)
    def delete_file(self, object_name: str, bucket: str = None) -> bool:
        """Delete file from MinIO"""
        try:
            bucket = bucket or self.bucket_name
            self.client.remove_object(bucket, object_name)
            print(f"File '{object_name}' deleted successfully from '{bucket}'")
            return True
        except S3Error as e:
            print(f"Error deleting file: {e}")
            return False
    
    @retry_on_connection_error(max_retries=3, delay=2)
    def list_objects(self, prefix: str = "", bucket: str = None) -> list:
        """List objects in bucket"""
        try:
            bucket = bucket or self.bucket_name
            objects = self.client.list_objects(bucket, prefix=prefix)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            print(f"Error listing objects: {e}")
            return []
    
    def get_object_url(self, object_name: str, bucket: str = None) -> str:
        """Get public direct URL for object"""
        bucket = bucket or self.bucket_name
        return f"http://{settings.MINIO_EXTERNAL_ENDPOINT}/{bucket}/{object_name}"
    
    @retry_on_connection_error(max_retries=3, delay=2)
    def get_object_url_download(self, object_name: str, expiration: int = 3600, bucket: str = None) -> str:
        """Get presigned URL for object download"""
        try:
            bucket = bucket or self.bucket_name
            url = self.external_client.presigned_get_object(
                bucket,
                object_name,
                expires=timedelta(seconds=expiration)
            )
            return url
        except S3Error as e:
            print(f"Error getting object URL: {e}")
            return None
    
    @retry_on_connection_error(max_retries=3, delay=2)
    def get_object_url_upload(self, object_name: str, expiration: int = 3600, bucket: str = None) -> str:
        """Get presigned URL for object upload"""
        try:
            bucket = bucket or self.bucket_name
            url = self.external_client.presigned_put_object(
                bucket,
                object_name,
                expires=timedelta(seconds=expiration)
            )
            return url
        except S3Error as e:
            print(f"Error getting upload URL: {e}")
            return None

# Global MinIO client instance
minio_client = MinIOClient()
