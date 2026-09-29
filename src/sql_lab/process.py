import os
import logging
import pandas as pd
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)

type_mapping = {
    "int64": "BIGINT",
    "int32": "INT",
    "float64": "DOUBLE",
    "bool": "TINYINT(1)",
    "datetime64[ns]": "DATETIME",
    "object": "VARCHAR(255)",  # safe default varchar length
    "string": "VARCHAR(255)",
}

#load envs
dbhost = os.getenv("DB_HOST")
dbname = os.getenv("DB_NAME")
dbuser = os.getenv("DB_USER")
dbpassword = os.getenv("DB_PASSWORD")

def read_data(filename):
    '''loads the CSV into a pandas DataFrame'''
    data = pd.read_csv(filename)
    logger.info("read %d rows from %s", len(data), filename)
    return data


def clean_data(data):
    '''prepares the DataFrame for upload (e.g., handle missing values, rename columns, cast types)'''
    cleaned = data.dropna()  # drop any row with a missing value
    logger.info("dropped %d rows with missing values", len(data) - len(cleaned))
    return cleaned

def load_data(data, table):
    '''writes the DataFrame to MySQL, creating the table if it doesn't exist'''
    engine = create_engine(
        f"mysql+mysqlconnector://{dbuser}:{dbpassword}@{dbhost}/{dbname}"
    )
    try:
        # to_sql creates the table and bulk-inserts the DataFrame
        data.to_sql(table, engine, if_exists="append", index=False)
        logger.info("loaded %d rows into `%s`", len(data), table)
    except Exception:
        logger.exception("failed to load data into `%s`", table)
    finally:
        engine.dispose()


def main():
    '''reads, cleans, and loads the mock dataset into MySQL'''
    data = read_data("MOCK_DATA.csv")
    cleaned = clean_data(data)
    load_data(cleaned, "mock")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

