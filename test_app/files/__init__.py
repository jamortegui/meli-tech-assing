import os
import uuid
import codecs

from flask import Blueprint, request, current_app, send_file, url_for
from werkzeug.utils import secure_filename

from test_app.processor import Processor
from test_app import settings
from .processing_functions import allowed_file, process_file


bp = Blueprint('files', __name__)


@bp.route('/upload', methods=['POST'])
def upload_file_endpoint():
    # Receives a file and its read configuration, ands starts file processing in the background

    # check if the post request has the file part
    if 'file' not in request.files:
        return {"error": "File not provided"}, 400
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        return {"error": "File not provided"}, 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename = str(uuid.uuid4()) + "." + filename.split(".")[-1].lower()
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        delimeter = request.form.get("delimeter") if request.form.get("delimeter") is not None else settings.DEFAULT_DELIMITER
        encoding = request.form.get("encoding") if request.form.get("encoding") is not None else settings.DEFAULT_ENCODING
        update = request.form.get("update") if request.form.get("update") is not None else settings.DEFAULT_UPDATE_REGISTERS
        update = False if update in ["FALSE", "false", "False", 0, "0", False] else True

        try:
            codecs.lookup(encoding)
        except LookupError:
            return {"error": "The provided encoding param is not valid."}, 400

        processor = Processor(process_file)
        processor.lauch_task(filename, delimeter, encoding, update)

        return {"file_key": filename}, 200
    
    return {"error": "The file format is not supported"}, 400


@bp.route('/status/<string:filename>', methods=['GET'])
def check_file_processing_status(filename):
    # Validates if the given filename has already been processed based on current available files.

    filename = secure_filename(filename)
    file_path = os.path.join(current_app.config.get("UPLOAD_FOLDER"), filename)
    errors_filename = filename.split(".")[0] + "_errors.jsonl"
    error_file_path = os.path.join(current_app.config.get("UPLOAD_FOLDER"), errors_filename)

    if not os.path.isfile(file_path) and not os.path.isfile(error_file_path):
        return {"error": "No initiated process was found for the given filename"}, 404
    elif not os.path.isfile(file_path) and os.path.isfile(error_file_path):
        return {"status": "completed", "errors": url_for('files.download_error_file', filename=errors_filename)}, 200
    else:
        return {"status": "processing"}, 102


@bp.route('/download/<string:filename>', methods=['GET'])
def download_error_file(filename):
    filename = secure_filename(filename)
    if not filename.endswith("_errors.jsonl"):
        return {"error": "The file name is not valid"}, 400
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.isfile(file_path):
        return {"error": "The requested file is not available"}, 404

    file = open(file_path, "rb")
    return send_file(file, as_attachment=True, download_name="errors.jsonl"), 200


@bp.route('/process_test_file', methods=['GET'])
def process_test_file_endpoint():
    # Processes "technical_challenge_data.csv" test file and returns its errors download link

    filename = "technical_challenge_data.csv"

    delimeter = settings.DEFAULT_DELIMITER
    encoding = settings.DEFAULT_ENCODING
    update = settings.DEFAULT_UPDATE_REGISTERS
    update = False if update in ["FALSE", "false", "False", 0, "0", False] else True

    try:
        codecs.lookup(encoding)
    except LookupError:
        return {"error": "The provided encoding param is not valid."}, 400
    
    errors_filename = process_file(filename, delimeter, encoding, update, delete_file=False)

    return {"status": "completed", "errors": url_for('files.download_error_file', filename=errors_filename)}, 200
