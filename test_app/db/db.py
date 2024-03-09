import psycopg2
from psycopg2.extras import execute_values

from test_app import settings


def get_db_connection(db_config=settings.DATABASE):
    # Creates a new connection to the db
    conn = psycopg2.connect(
        dbname=db_config.get("NAME"),
        user=db_config.get("USER"),
        password=db_config.get("PASSWORD"),
        host=db_config.get("HOST"),
        port=db_config.get("PORT")
    )

    return conn


def is_in_db(cursor, data):
    # Construct the WHERE clause dynamically based on the validation data
    where_clause = ' AND '.join([f"{key} = %s" for key in data.keys()])

    # Get the values to pass to the query
    values = tuple(data.values())

    sql_query = f"SELECT COUNT(*) FROM items WHERE {where_clause}"
    cursor.execute(sql_query, values)
    count = cursor.fetchone()[0]

    return count != 0


def save_data(cursor, data, errors):
    '''
    cursor = The active database cursor to perform the commands
    data = List of dictionaries containing the data to be inserted in the db
    errors = List of dictionaries containing info about errors processing the current data chunk
    '''
    if not data:
        return errors
    # Get columns from the first row
    columns = list(data[0].keys())

    # Construct the INSERT query dynamically for multiple rows
    insert_columns = ', '.join(columns)

    # Flatten values from all rows
    values = []
    for row in data:
        try:
            row_values = [row[column] for column in columns]
            values += row_values
        except KeyError:
            errors.append({"error": "The data is incomplete and cant be saved in the database", "row": row})

    insert_values = ', '.join(['(' + ', '.join(['%s'] * len(columns)) + ')'] * (len(values) // len(columns)))
    insert_query = f"INSERT INTO items ({insert_columns}) VALUES {insert_values}"

    # Execute the INSERT query
    cursor.execute(insert_query, values)

    return errors


def update_data(cursor, data, errors, key_columns=settings.FILE_KEYS):
    '''
    cursor = The active database cursor to perform the commands
    data = List of dictionaries containing the data to be inserted in the db
    errors = List of dictionaries containing info about errors processing the current data chunk
    key_columns = Dictionary of the form {column_name:column_dtype} where keys are the columns that will be used to
    query the row that needs to be updated.
    '''
    if not data:
        return errors
    # Uses Psycopg execute_values to perform multiple UPDATE commands dinamically constructed based on data info
    columns = list(data[0].keys())
    values_columns = ", ".join(columns)
    insert_values = ", ".join(f"{column}=data.{column}" for column in columns if column not in key_columns.keys())
    where_query = " AND ".join(f"items.{column} = data.{column}" for column in key_columns.keys())

    sql_query = f"UPDATE items SET {insert_values} FROM (VALUES %s) AS data ({values_columns}) WHERE {where_query}"

    values = []
    for row in data:
        try:
            row_values = [row[column] for column in columns]
            values.append(row_values)
        except KeyError:
            errors.append({"error": "The data is incomplete and cant be saved in the database", "row": row})

    execute_values(cursor, sql_query, values)

    return errors
