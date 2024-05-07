import os
import snowflake.connector
from dotenv import load_dotenv


def connect_to_snowflake():
    print("I am here")
    conn = snowflake.connector.connect(
        user="klsayushvaish",
        password="KLSAyushVaish2511",
        account="sa23173.ap-southeast-1",
        database="SAMPLE",
        schema = "PUBLIC" 
    )
    return conn