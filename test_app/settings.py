# General app setup

# Database settings
DATABASE = {
    "NAME": 'postgres',
    "USER": 'postgres',
    "PASSWORD": 'postgres',
    # NOTE: These credentials are being hardcoded for the example, however, in a real-life scenario they should never be committed to a git repository.
    "HOST": 'db',
    "PORT": '5001',
}
INIT_SCHEMA = "db/schemas/schema.sql"  # SQL file to initialize the DB

# File processing settings
UPLOAD_FOLDER = "./user_uploads/"  # Folder where files will be uploaded
ALLOWED_EXTENSIONS = ["txt", "csv", "jsonl"]  # Supported file extentions
THREADS_PER_FILE = 50  # Number of threads to create the Thread pool
DEFAULT_DELIMITER = ","  # Default delimiter to parse CSV and TXT files
DEFAULT_ENCODING = "utf-8"  # Default encoding to read uploaded files
FILE_KEYS = {
    "site": str,
    "id": int,
}  # Expected file heades and data types
CHUNK_SIZE = 20  # Number of rows to process in a single items API call
DEFAULT_UPDATE_REGISTERS = False  # Wheter or not to update info form items that are already in our database

# MeLi API interaction settings
RETRY_WAIT_TIME = 1  # Time to wait beetween a failed API call and its retry.
MAX_RETRIES = 5  # Max number of retrys for a failed API call.

ATTRIBUTES_TO_RETRIEVE = ["price", "start_time", "category_id", "currency_id", "seller_id"]  # Attributes of interest from items API
ITEMS_API_URL = "https://api.mercadolibre.com/items?ids={}&attributes=id,{}"
USERS_API_URL = "https://api.mercadolibre.com/users?ids={}"
CURRENCIES_API_URL = "https://api.mercadolibre.com/currencies/{}"
CATEGORIES_API_URL = "https://api.mercadolibre.com/categories/{}"
