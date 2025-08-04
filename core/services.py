from fastapi import FastAPI, UploadFile, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi import status
import os
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

BASE_DIR: str = "uploads/"
MEDIA_URL: str = "https://image-management-bucket.fly.storage.tigris.dev/"

client = boto3.client(
    "s3",
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    endpoint_url=os.environ["AWS_ENDPOINT_URL_S3"],
    config=Config(s3={"addressing_style": "path"}),
)


# define a function that takes the folder name and key
def construct_url(**kwargs):
    if 'folder_name' in kwargs and 'key' in kwargs:
        return f"{MEDIA_URL}{kwargs['folder_name']}/{kwargs['key']}"
    return f"{MEDIA_URL}{kwargs['key']}"
    

def get_media(filename: str, media_type: str):
    try:
        from pprint import pprint
        file_obj = client.get_object(
            Bucket=os.environ["AWS_BUCKET_S3"], Key=f"{media_type}s/{filename}"
        )
        pprint(file_obj)
    except ClientError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{media_type} does not exist"
        )
    else:
        return {"url": construct_url(folder_name=f"{media_type}s", key=filename)}

def get_all_media(folder_name: str):
    #get all media objects from specified folder
    media_objects = client.list_objects_v2(
        Bucket=os.environ["AWS_BUCKET_S3"], Prefix=f"{folder_name}s"
    )["Contents"]
    
    from pprint import pprint
    pprint(media_objects)
    
    # store urls in list
    media_urls = []
    for each in media_objects:
        url = construct_url(key=each['Key'])
        media_urls.append(url)

    return {f"{folder_name}": media_urls}
