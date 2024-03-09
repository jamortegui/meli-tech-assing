from .csv_reader import read_csv
from .jsonl_reader import read_jsonl
from .txt_reader import read_txt


FILE_READERS = {
        "jsonl": read_jsonl,
        "txt": read_txt,
        "csv": read_csv,
}  # File reader functions for each supported file extention


def get_file_reader(file_format):
    # Decides which file reader to use based on file extention.
    file_format = file_format.lower()
    return FILE_READERS.get(file_format)
