from test_app import settings


def read_txt(txt_file_path, delimeter, encoding):
    with open(txt_file_path, mode='r', encoding=encoding) as file:
        headers = []
        chunk = []

        for i, line in enumerate(file):
            row = line.strip().split(delimeter)
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
