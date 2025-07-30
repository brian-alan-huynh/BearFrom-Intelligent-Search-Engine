import os
import uuid
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from fastapi import UploadFile, HTTPException

load_dotenv()
env = os.getenv

class S3Storage:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=env('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=env('AWS_SECRET_ACCESS_KEY'),
            region_name=env('AWS_REGION', 'us-west-2')
        )

        self.bucket_name = env('S3_BUCKET_NAME')
        self.presigned_url_expiry = 3600  # 1 hour

    def generate_pfp_key(self, user_id: int, filename: str) -> str:
        file_extension = os.path.splitext(filename)[1].lower()
        unique_id = str(uuid.uuid4())
        timestamp = int(datetime.now().timestamp())

        return f"users/{user_id}/profile_pictures/{timestamp}_{unique_id}{file_extension}"

    async def upload_pfp(self, user_id: int, file: UploadFile) -> str:
        """
        Upload a profile picture to S3 and return the S3 key.
        
        Args:
            user_id: The ID of the user
            file: FastAPI UploadFile object containing the image
            
        Returns:
            str: The S3 key for the uploaded file
        """
        try:
            file_extension = os.path.splitext(file.filename)[1].lower()
            
            if file_extension not in ['.jpg', '.jpeg', '.png', '.gif']:
                return "Invalid file type. Only JPG, JPEG, PNG, and GIF are allowed."
                
            s3_key = self.generate_pfp_key(user_id, file.filename)
            
            file_content = await file.read()
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=file.content_type,
                ACL='public-read'
            )
            
            return s3_key # After calling this function, store this key in the User table at pfp_key column
            
        except ClientError:
            return "Failed to upload profile picture to S3"

    # The returned URL is a temporary S3 link that can be used in <img src="url"> tags
    def get_pfp_url(self, s3_key: str) -> str:
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=self.presigned_url_expiry
            )

            return url
            
        except ClientError:
            return "Failed to retrieve profile picture"
    
    def delete_pfp(self, s3_key: str) -> bool:
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )

            return True

        except ClientError:
            return "Failed to remove profile picture"

storage = S3Storage()
