from fastapi import FastAPI, UploadFile, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi import status
import os
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from main import BASE_DIR, app


@app.get("/get-image/{filename}")
def get_image(filename: str = None):
    file_path = os.path.join(BASE_DIR, filename)

    # check if file exists
    # if not os.path.isfile(file_path):
    if not os.path.isfile(file_path):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Image does not exist")

    return FileResponse(file_path)


@app.get("/get-all-images")
def get_all_images(request: Request):
    all_images = os.listdir(BASE_DIR)
    image_urls = []
    for image in all_images:
        # use request.url_for() to format urls
        img_url = str(request.url_for("get_image", filename=image))
        image_urls.append(img_url)

    return {"urls": image_urls}


@app.post("/upload-image")
async def upload_image(file: UploadFile):
    file_path = os.path.join(BASE_DIR, file.filename)

    # use context manager to handle file
    with open(file_path, "wb") as f:
        # store the image request file by reading and writing
        f.write(await file.read())
        file.close()

    return {
        "message": f"{file.filename} successfully uploaded",
    }


# what I observed from this project
# What you work with depends on project requirements
# This project requires file handling and using file paths

# os.path
# os.path.isfile
