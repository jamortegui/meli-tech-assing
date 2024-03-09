import json

from test_app import settings


def read_jsonl(jsonl_file_path, delimeter, encoding):
    with open(jsonl_file_path, mode='r', encoding=encoding) as file:
        chunk = []
        for line in file:
            chunk.append(json.loads(line))
            if len(chunk) < settings.CHUNK_SIZE:
                continue
            else:
                yield chunk
                chunk = []
        yield chunk
