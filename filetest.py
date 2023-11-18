import os

import boto3
import uuid


def upload_file(file: str, folder_name: str):
    try:
        # s3 클라이언트 생성
        s3 = boto3.client(
            service_name="s3",
            region_name="ap-northeast-2",
            aws_access_key_id=os.environ["S3_ACCESS"],
            aws_secret_access_key=os.environ["S3_SECRET"],
        )
    except Exception as e:
        print(e)
    else:
        with open("FILE_NAME", "rb") as f:
            _, file_extension = os.path.splitext(file)
            random_file_name = f"{folder_name}/{str(uuid.uuid4()) + file_extension}"
            s3.upload_fileobj(f, "BUCKET_NAME", "OBJECT_NAME")
        s3.upload_fileobj(file, "dangmuzi-photo", random_file_name)
        return "https://dangmuzi-photo.s3.ap-northeast-2.amazonaws.com/"+random_file_name