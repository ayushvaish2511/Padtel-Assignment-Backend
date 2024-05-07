# Importing necessary modules
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

# Dependency to get Snowflake connection
def get_snowflake_conn():
    return snowflake.connect_to_snowflake()

# Function to generate a random app secret token
def generate_app_secret_token():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(32))  # Generate a 32-character token

# Function to handle incoming data and send it to destinations
@router.post("/server/incoming_data")
def handle_incoming_data(data: Dict[str, Any], secret_token: str = Header(...), conn=Depends(get_snowflake_conn)):
    # Check if secret token is provided
    if not secret_token:
        raise HTTPException(status_code=401, detail="Unauthenticated: Secret token missing")

    # Authenticate the secret token and get the account ID
    account_id = authenticate_secret_token(secret_token, conn)
    print('got_id', account_id)
    # Validate the incoming data
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Invalid Data: JSON data expected")

    # Retrieve destinations available for the account
    destinations = get_destinations_for_account(account_id, conn)

    # Send data to each destination
    for destination in destinations:
        send_data_to_destination(destination, data)

    return {"message": "Data sent to destinations successfully"}

# Function to authenticate the secret token and retrieve the account ID
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

# Function to retrieve destinations available for the given account ID
# Update the get_destinations_for_account function
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
    # Prepare request headers
    headers = json.loads(destination['headers'])
    
    # Validate HTTP method
    http_method = destination.get('http_method', '').upper()
    if http_method not in ['GET', 'POST', 'PUT', 'DELETE']:
        raise ValueError(f"Unsupported HTTP method: {http_method}")

    # Add the scheme to the URL if missing
    url = destination['url']
    if not url.startswith('http://') and not url.startswith('https://'):
        url = f'http://{url}'

    # Send data based on HTTP method
    if http_method == "GET":
        # Append data as query parameters
        response = requests.get(url, params=data, headers=headers)
    elif http_method in ["POST", "PUT"]:
        # Send data as JSON payload
        response = requests.request(http_method, url, json=data, headers=headers)
    else:
        # Unsupported HTTP method   
        raise ValueError(f"Unsupported HTTP method: {http_method}")

    # Check response status
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=f"Failed to send data to destination: {url}")
