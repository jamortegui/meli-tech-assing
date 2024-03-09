import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from collections import Counter
import asyncio
import json

from .file_readers import get_file_reader
from test_app.db.db import get_db_connection, is_in_db, save_data, update_data
from test_app.meli_api import get_items_basic_info, get_items_complement_info
from test_app import settings


def allowed_file(filename):
    # Validates if uploaded file extention is supported

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS


def check_lines_valid(lines, update_registers, db_cursor):
    # For each row in the rows chunk, validates correct header names, data types and checks if the item is already in the DB

    valid_lines = []
    errors = []
    for line in lines:
        if not Counter(line.keys()) == Counter(settings.FILE_KEYS.keys()):
            errors.append({"error": "Incorrect file headers", "row": line})
            continue
        try:
            line = {key: settings.FILE_KEYS[key](value) for key, value in line.items()}
        except ValueError:
            errors.append({"error": "Incorrect value type", "row": line})
            continue
        if update_registers or not is_in_db(db_cursor, line):
            valid_lines.append(line)

    return valid_lines, errors


def split_update_lines(lines, db_cursor, line_headers=settings.FILE_KEYS):
    # Given a chunk of rows, splits the chunck betweenitems that are already in DB and items that doesnt.

    lines_to_update = []
    lines_to_insert = []

    for line in lines:
        simplified_line = {key: line[key] for key in line_headers.keys()}
        if is_in_db(db_cursor, simplified_line):
            lines_to_update.append(line)
        else:
            lines_to_insert.append(line)

    return lines_to_update, lines_to_insert


def process_file_line(lines, update_registers):
    # Gathers the required information for a given items chunk and stores the in the database

    db_con = get_db_connection()
    cursor = db_con.cursor()

    lines, errors = check_lines_valid(lines, update_registers, cursor)

    lines, errors = get_items_basic_info(lines, errors)

    _ = asyncio.run(get_items_complement_info(lines))

    if update_registers:
        lines_to_update, lines_to_insert = split_update_lines(lines, cursor)
        errors = save_data(cursor, lines_to_insert, errors)
        errors = update_data(cursor, lines_to_update, errors)
    else:
        errors = save_data(cursor, lines, errors)

    db_con.commit()
    db_con.close()
    return errors


def process_file(filename, delimeter, encoding, update_registers, delete_file=True):
    # Given a filename and read setup, devides the file in chunks and initializes the Thread pool to process each chunk concurrently
    # At the same time, generates corresponding errors file.

    excecutor = ThreadPoolExecutor(settings.THREADS_PER_FILE)
    file_extention = filename.split(".")[-1]
    file_path = os.path.join(settings.UPLOAD_FOLDER, filename)
    file_reader = get_file_reader(file_extention)

    results = excecutor.map(partial(process_file_line, update_registers=update_registers), file_reader(file_path, delimeter, encoding))

    errors_file_name = filename.split(".")[0] + "_errors.jsonl"
    errors_file_path = os.path.join(settings.UPLOAD_FOLDER, errors_file_name)

    # Save JSON data as JSONL file
    with open(errors_file_path, 'w') as jsonl_file:
        for errors in results:
            for error in errors:
                jsonl_file.write(f"{json.dumps(error)}\n")

    if delete_file:
        os.remove(file_path)

    return errors_file_name
