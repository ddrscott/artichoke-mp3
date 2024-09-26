import hashlib
import logging
import os
import json
from io import BytesIO

import functions_framework
from flask import Response
import requests
from google.cloud import storage

from pydantic import BaseModel

class SummaryRequest(BaseModel):
    url: str
    voice: str = 'nova'

@functions_framework.http
def summary(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """

    req = SummaryRequest(**request.get_json(silent=True))

    # Generate MD5 hash of URL and voice
    md5sum = hashlib.md5(f"{req.url}{req.voice}".encode()).hexdigest()
    bucket_name = os.getenv('BUCKET_NAME')
    summary_path = f"artichoke/summary/{md5sum}.json"
    mp3_path = f"artichoke/summary/{md5sum}.mp3"

    # Initialize Google Cloud Storage client
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Check if the summary JSON already exists
    summary_blob = bucket.blob(summary_path)
    if summary_blob.exists():
        logging.info(f"Found existing summary for {md5sum}")
        summary_data = json.loads(summary_blob.download_as_text())
        return Response(json.dumps(summary_data), content_type='application/json')

    # Generate new summary and text-to-speech response
    logging.info(f"Generating script for {req}")
    script = fetch_summary(req.url)
    logging.info(f"Script generated: {script}")

    speech_response = convert_text_to_speech(script, voice=req.voice)

    # Save the MP3 to Google Cloud Storage
    mp3_blob = bucket.blob(mp3_path)
    mp3_data = BytesIO(speech_response.content)
    mp3_blob.upload_from_file(mp3_data, content_type=speech_response.headers['Content-Type'])

    # Create the response JSON
    response_data = {
        "url": req.url,
        "voice": req.voice,
        "script": script,
        "mp3": f"https://{bucket_name}/{mp3_path}"
    }

    # Save the response JSON to Google Cloud Storage
    summary_blob.upload_from_string(json.dumps(response_data), content_type='application/json')

    return Response(json.dumps(response_data), content_type='application/json')

def convert_text_to_speech(input_text, model='tts-1', voice='nova'):
    url = "https://api.openai.com/v1/audio/speech"
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "input": input_text,
        "voice": voice
    }

    response = requests.post(url, headers=headers, json=data, stream=True)

    if response.status_code != 200:
        logging.error(f"Request failed with status code {response.status_code} and response text {response.text}")
        raise Exception(f"Request failed with status code {response.status_code} and response text {response.text}")

    return response

SUMMARY_PROMPT = """\
Act as a youthful podcaster. Write a concise, naturally spoken, and engaging summary with an insight for your tech savvy audience start with the hook: Ever ...
"""

def fetch_summary(url):
    EXA_API_KEY = os.getenv('EXA_API_KEY')

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-key": EXA_API_KEY
    }

    data = {
        "ids": [url],
        "summary": {
            "query": SUMMARY_PROMPT
        }
    }

    response = requests.post('https://api.exa.ai/contents', headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        results = response.json().get('results', [])
        for result in results:
            return result.get('summary', 'No summary found')
    else:
        logging.error(f"Request failed with status code {response.status_code} and response text {response.text}")
        raise Exception(f"Request failed with status code {response.status_code} and response text {response.text}")
