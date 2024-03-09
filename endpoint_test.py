import requests
import time

# File to process
FILE_PATH = r"d:\Documentos\MercadoLibre\tech_assingment\technical_challenge_data.csv"

# API endpoint URLs
UPLOAD_ENDPOINT = 'http://localhost:5000//upload'
STATUS_ENDPOINT = "http://localhost:5000//status/{}"
ROOT = "http://localhost:5000/"

# FIle reading setup
ENCODING = "utf-8"
DELIMETER = ","
UPDATE = False

MAX_STATUS_RETRIES = 50

# Send the file and setup payload to the API
with open(FILE_PATH, 'rb') as f:
    files = {'file': f}
    data = {"encoding": ENCODING,
            "delimeter": DELIMETER,
            "update": UPDATE}
    response = requests.post(UPLOAD_ENDPOINT, files=files, data=data)

# Check the response
if response.status_code == 200:
    filename_key = response.json().get("file_key")
    response = requests.get(STATUS_ENDPOINT.format(filename_key))
    retries = 0
    while not response.status_code == 200 and retries <= MAX_STATUS_RETRIES:
        retries += 1
        print("Response not ready yet")
        time.sleep(1)
        response = requests.get(STATUS_ENDPOINT.format(filename_key))
    download_url = ROOT + response.json().get("errors")
    response = requests.get(download_url)
    if response.status_code == 200:
        with open("downloaded_files/errors.jsonl", 'wb') as f:
            f.write(response.content)
        print("Execution completed and file saved successfully.")
    else:
        print("Failed to download errors file.")
else:
    print('Error:', response.json().get('error'))
