import os
import logging
import pandas as pd
import mysql.connector
logger = logging.getLogger(__name__)

#load envs 
dbhost = os.getenv("DB_HOST")
dbname = os.getenv("DB_NAME")
dbuser = os.getenv("DB_USER")
dbpassword = os.getenv("DB_PASSWORD")


def _connect():
    '''opens a connection to the mock database'''
    #connect using the env-var credentials loaded above
    return mysql.connector.connect(
        host=dbhost, database=dbname, user=dbuser, password=dbpassword
    )


def get_data_by_group(value):
    '''returns all rows from `mock` where the `group` column equals value'''
    query = "SELECT * FROM mock WHERE `group` = %s"
    conn = None
    try:
        conn = _connect()  #open connection
        cursor = conn.cursor()
        cursor.execute(query, (value,)) 
        results = cursor.fetchall()  #pull matching rows
        logger.info("found %d rows for group=%s", len(results), value)
        return results
    except mysql.connector.Error:
        logger.exception("failed to query mock by group=%s", value)
        return None
    finally:
        if conn is not None and conn.is_connected():
            cursor.close()  #release cursor
            conn.close()  #close connection


def plot_counts(groupby):
    '''counts rows in `mock` per distinct value of the given groupby column'''
    query = f"SELECT `{groupby}`, COUNT(*) FROM mock GROUP BY `{groupby}`"
    conn = None
    try:
        conn = _connect()  #open connection
        cursor = conn.cursor()
        cursor.execute(query)  #run the GROUP BY count
        results = cursor.fetchall()  #pull one row per distinct value
        counts = pd.DataFrame(results, columns=[groupby, "count"]) 
        logger.info("counted %d distinct %s values", len(counts), groupby)
        return counts
    except mysql.connector.Error:
        logger.exception("failed to count rows by %s", groupby)
        return None
    finally:
        if conn is not None and conn.is_connected():
            cursor.close()  #release cursor
            conn.close()  #close connection


def main():
    '''demonstrates the query functions against the mock table'''
    print("=== rows where group = group1 ===")
    print(get_data_by_group("group1"))  #filter demo

    print("=== counts by group ===")
    print(plot_counts("group"))  #aggregate demo


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
