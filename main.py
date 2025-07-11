from fastapi import FastAPI, UploadFile, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi import status
import os
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

# create FastAPI object
app = FastAPI()

BASE_DIR = "uploads/"
IMAGE_URL = "https://image-management-bucket.fly.storage.tigris.dev/"

# Create client for Tigris
client = boto3.client(
    "s3",
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    endpoint_url=os.environ["AWS_ENDPOINT_URL_S3"],
    config=Config(s3={"addressing_style": "path"}),
)

# helper method
# def gen_presigned_url(key: str) -> str:
#     presigned_url: str = client.generate_presigned_url(
#         ClientMethod="get_object",
#         Params={
#             "Bucket": os.environ["AWS_BUCKET_S3"],
#             "Key": key,
#             "ResponseContentType": "image/jpeg"
#             },
#         ExpiresIn=3600,
#         HttpMethod=None,
#         )
#     return presigned_url


# list image objects


# api routes
@app.get("/get-image/{filename}")
def get_image(filename: str = None):
    try:
        from pprint import pprint
        file_obj = client.get_object(Bucket=os.environ['AWS_BUCKET_S3'], Key=filename)
        pprint(file_obj)
    except ClientError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image does not exist")
    else:
        return {"url": f"{IMAGE_URL}{filename}"}


@app.get("/get-all-images")
def get_all_images(request: Request):
    image_objects = client.list_objects_v2(Bucket=os.environ["AWS_BUCKET_S3"])[
        "Contents"
    ]
    # store urls in list
    image_urls = []

    for each in image_objects:
        url = f"{IMAGE_URL}{each['Key']}"
        image_urls.append(url)

    return {"images": image_urls}


@app.post("/upload-image")
async def upload_image(file: UploadFile):
    # add image to bucket
    client.put_object(
        Body=await file.read(),
        Bucket=os.environ["AWS_BUCKET_S3"],
        Key=file.filename,
        ContentDisposition=f"inline; filename{file.filename}",
        ContentType=f"{file.content_type}",
        ContentLength=file.size,
        ACL="public-read",
    )

    print(file)

    return JSONResponse(
        {
            "message": f"{file.filename} successfully uploaded",
            "link": f"{IMAGE_URL}{file.filename}",
        },
        status_code=status.HTTP_201_CREATED,
    )


# @app.get("/get-image/{filename}")
# def get_image(
#     filename: str = None
#     ):
#     file_path = os.path.join(BASE_DIR, filename)

#     # check if file exists
#     # if not os.path.isfile(file_path):
#     if not os.path.isfile(file_path):
#         raise HTTPException(status.HTTP_404_NOT_FOUND, "Image does not exist")

#     return FileResponse(file_path)


# @app.get("/get-all-images")
# def get_all_images(request: Request):
#     all_images = os.listdir(BASE_DIR)
#     image_urls = []
#     for image in all_images:

#         #use request.url_for() to format urls
#         img_url = str(request.url_for("get_image", filename=image))
#         image_urls.append(img_url)

#     return {"urls": image_urls}


# @app.post("/upload-image")
# async def upload_image(file: UploadFile):
#     file_path = os.path.join(BASE_DIR, file.filename)

#     # use context manager to handle file
#     with open(file_path, "wb") as f:
#         # store the image request file by reading and writing
#         f.write(await file.read())
#         file.close()

#     return {
#         "message": f"{file.filename} successfully uploaded",
#     }


# what I observed from this project
# What you work with depends on project requirements
# This project requires file handling and using file paths

# os.path
# os.path.isfile
