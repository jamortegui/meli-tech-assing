import csv

from test_app import settings


def read_csv(csv_file_path, delimeter, encoding):
    with open(csv_file_path, mode='r', newline='', encoding=encoding) as file:
        csv_reader = csv.reader(file, delimiter=delimeter)
        headers = []
        chunk = []
        for i, row in enumerate(csv_reader):
            if i == 0:
                headers = row
                continue
            else:
                chunk.append({name: value for name, value in zip(headers, row)})
            if len(chunk) < settings.CHUNK_SIZE:
                continue
            else:
                yield chunk
                chunk = []
        yield chunk
