import secrets
import string
from fastapi import APIRouter, Depends, Header, HTTPException
from typing import List, Dict, Any
import requests
import json

from app.models import destination as schemas
from app.models import account
from app.db import snowflake

from snowflake.connector import DictCursor

router = APIRouter()

def get_snowflake_conn():
    return snowflake.connect_to_snowflake()

@router.post("/server/incoming_data")
def handle_incoming_data(data: Dict[str, Any], secret_token: str = Header(...), conn=Depends(get_snowflake_conn)):
    
    if not secret_token:
        raise HTTPException(status_code=401, detail="Unauthenticated: Secret token missing")

    
    account_id = authenticate_secret_token(secret_token, conn)
    print('got_id', account_id)
  
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Invalid Data: JSON data expected")

    destinations = get_destinations_for_account(account_id, conn)

    for destination in destinations:
        send_data_to_destination(destination, data)

    return {"message": "Data sent to destinations successfully"}

def authenticate_secret_token(secret_token: str, conn):
    query = "SELECT account_id FROM accounts WHERE app_secret_token = %(secret_token)s"
    with conn.cursor() as cur:
        cur.execute(query, {"secret_token": secret_token})
        result = cur.fetchone()
        if result is None:
            raise HTTPException(status_code=401, detail="Unauthenticated: Invalid secret token")
        return result[0]


def map_keys(destination_data: dict) -> dict:
    mapped_data = {
        "destination_id": destination_data.get("DESTINATION_ID"),
        "url": destination_data.get("URL"),
        "http_method": destination_data.get("HTTP_METHOD"),
        "headers": destination_data.get("HEADERS"),
        "account_id": destination_data.get("ACCOUNT_ID")
    }
    return mapped_data

def get_destinations_for_account(account_id: int, conn):
    query = "SELECT * FROM destinations WHERE account_id = %(account_id)s"
    with conn.cursor(DictCursor) as cur:
        cur.execute(query, {"account_id": account_id})
        destinations = cur.fetchall()
        resp = []
        for destination in destinations:
            mapped_data = {
                "destination_id": destination.get("DESTINATION_ID"),
                "url": destination.get("URL"),
                "http_method": destination.get("HTTP_METHOD"),
                "headers": destination.get("HEADERS"),
                "account_id": destination.get("ACCOUNT_ID")
            }
            resp.append(mapped_data)

        return resp


def parse_headers(headers_str: str) -> Dict[str, str]:
    headers_dict = json.loads(headers_str)
    return {key.lower(): value for key, value in headers_dict.items()}
    
def send_data_to_destination(destination: dict, data: dict):
 
    headers = json.loads(destination['headers'])
    

    http_method = destination.get('http_method', '').upper()
    if http_method not in ['GET', 'POST', 'PUT', 'DELETE']:
        raise ValueError(f"Unsupported HTTP method: {http_method}")

    url = destination['url']
    if not url.startswith('http://') and not url.startswith('https://'):
        url = f'http://{url}'

    if http_method == "GET":
        response = requests.get(url, params=data, headers=headers)
    elif http_method in ["POST", "PUT"]:
        response = requests.request(http_method, url, json=data, headers=headers)
    else:
        raise ValueError(f"Unsupported HTTP method: {http_method}")

    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=f"Failed to send data to destination: {url}")
