# Example snowflake.py


# https://sa23173.ap-southeast-1.snowflakecomputing.com
# WASKKLQ.AO22303

import os
import snowflake.connector
from dotenv import load_dotenv


def connect_to_snowflake():
    # Connect to Snowflake database
    # return connect(user='your_user', password='your_password', account='your_account', warehouse='your_warehouse', database='your_database', schema='your_schema')
    print("I am here")
    conn = snowflake.connector.connect(
        user="klsayushvaish",
        password="KLSAyushVaish2511",
        account="sa23173.ap-southeast-1",
        database="SAMPLE",
        schema = "PUBLIC" 
    )
    return conn
    # if conn:
    #     print("Success")
    # else :
    #     print("Not")
    # return conn

# connect_to_snowflake()