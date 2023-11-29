from flask import Flask, request

import os
import uuid
import requests
import base64
import boto3
import io

S3_BUCKET="gptactionhub-stabilityai"
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", None)
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", None)
AWS_DEFAULT_REGION = os.environ.get("AWS_DEFAULT_REGION", None)

app = Flask(__name__)

def get_s3():
    return boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    )

def upload_to_s3(file, filename):
    unique_filename = filename

    get_s3().upload_fileobj(file, S3_BUCKET, unique_filename)
    return unique_filename


def generate_random_filename(extension=".txt"):
    filename = str(uuid.uuid4()) + extension
    return filename

@app.route("/text-to-image", methods=['POST'])
def text_to_image():
    engine_id = "stable-diffusion-v1-6"

    api_host = 'https://api.stability.ai'
    api_key = os.getenv("STABILITY_API_KEY", None)
    if 'STABILITY_API_KEY' in request.headers:
        api_key = request.headers["STABILITY_API_KEY"]
    data = request.json
    if "height" not in data or data["height"] == "":
        data["height"]=400
    if "width" not in data or data["width"] == "":
        data["width"]=600

    if api_key is None:
        raise Exception("Missing Stability API key.")

    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "text_prompts": [
                {
                    "text": data["text"]
                }
            ],
            "cfg_scale": 7,
            "height": int(data["height"]),
            "width": int(data["width"]),
            "samples": 1,
            "steps": 30,
        },
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    d = response.json()

    furls = []
    for i, image in enumerate(d["artifacts"]):
        key = upload_to_s3(io.BytesIO(base64.b64decode(image["base64"])), generate_random_filename()+".png")
        furls.append(get_s3().generate_presigned_url('get_object', Params={'Bucket': S3_BUCKET, 'Key': key}, ExpiresIn=3600))

    return "!["+data["text"]+"]("+furls[0]+") Display this image inline for the user. Mention its generated from "+engine_id+". Include the full url and parameters."

@app.route('/', methods=['GET'])
def catch_all():
    return "ok"

if __name__ == '__main__':
    app.run(debug=True, port=10008, host="0.0.0.0")
