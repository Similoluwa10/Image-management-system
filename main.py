from fastapi import FastAPI, UploadFile, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi import status
import os
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from core.services import get_media, get_all_media

# create FastAPI object
app = FastAPI()

BASE_DIR: str = "uploads/"
MEDIA_URL: str = "https://image-management-bucket.fly.storage.tigris.dev/"


# Create client for Tigris
client = boto3.client(
    "s3",
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    endpoint_url=os.environ["AWS_ENDPOINT_URL_S3"],
    config=Config(s3={"addressing_style": "path"}),
)


# api routes
@app.post("/upload-media")
async def upload_media(file: UploadFile):
    #check file size
    # if file.size > 52428800:
    #     raise HTTPException(
    #         status_code=status.HTTP_406_NOT_ACCEPTABLE,
    #         detail="File size should not exceed 50MB",
    #     )
   
    # check if file is image or video
    key = ''
    print(f"CONTENT TYPE: {file.content_type}")
    
    if ["image/jpeg", "image/jpg", "image/png"].__contains__(file.content_type):
        key = f"images/{file.filename}"
        print(key)
    
    if file.content_type == "video/mp4":
        key = f"videos/{file.filename}"
        print(key)
        
    print(file.content_type)

    # add image to bucket
    client.put_object(
        Body=await file.read(),
        Bucket=os.environ["AWS_BUCKET_S3"],
        Key= key,
        ContentDisposition=f"inline; filename{file.filename}",
        ContentType=f"{file.content_type}",
        ContentLength=file.size,
        ACL="public-read",
        CacheControl="public, max-age=31536000"
    )
    from pprint import pprint
    pprint(file)

    return JSONResponse(
        {
            "message": f"{file.filename} successfully uploaded",
            "link": f"{MEDIA_URL}{file.filename}",
        },
        status_code=status.HTTP_201_CREATED,
    )


@app.get("/get-image/{filename}")
def get_image(filename: str = None):
    response = get_media(filename, "image")
    return response


@app.get("/get-video/{filename}")
def get_video(filename: str = None):
    response = get_media(filename, "video")
    return response


@app.get("/get-all-images")
def get_all_images(request: Request):
    response = get_all_media("image")
    return response


@app.get("/get-all-videos")
def get_all_videos(request: Request):
    response = get_all_media("video")
    return response
