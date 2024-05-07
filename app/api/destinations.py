import json
from fastapi import APIRouter, Depends, HTTPException
from snowflake.connector import DictCursor

from app.models import destination as schemas
from app.db import snowflake

router = APIRouter()

def get_snowflake_conn():
    return snowflake.connect_to_snowflake()

@router.post("/destinations/", response_model=int)
def create_destination(destination: schemas.DestinationCreate, conn=Depends(get_snowflake_conn)):
    """
    Create a new destination
    """
    query = """
    INSERT INTO destinations (url, http_method, headers, account_id)
    VALUES (%s, %s, %s, %s)
    """
    headers_json = json.dumps(destination.headers)
    with conn.cursor() as cur:
        cur.execute(query, (destination.url, destination.http_method, headers_json, destination.account_id))
        cur.execute("SELECT destination_id FROM destinations WHERE url = %s AND http_method = %s AND account_id = %s", (destination.url, destination.http_method, destination.account_id))
        destination_id = cur.fetchone()
        return destination_id[0]



@router.get("/destinations/{destination_id}/", response_model=schemas.DestinationResponse)
def get_destination(destination_id: int, conn=Depends(get_snowflake_conn)):
    """
    Get a destination by ID
    """
    query = "SELECT destination_id, url, http_method, headers, account_id FROM destinations WHERE destination_id = %s"
    with conn.cursor(DictCursor) as cur:
        cur.execute(query, (destination_id,))
        destination_data = cur.fetchone()
        print('destinationsss', destination_data)
        if destination_data is None:
            raise HTTPException(status_code=404, detail="Destination not found")
        return schemas.DestinationResponse(**destination_data)


@router.put("/destinations/{destination_id}/", response_model=schemas.Destination)
def update_destination(destination_id: int, destination: schemas.DestinationUpdate, conn=Depends(get_snowflake_conn)):
    """
    Update a destination by ID
    """
    existing_destination_query = "SELECT * FROM destinations WHERE destination_id = %(destination_id)s"
    with conn.cursor(DictCursor) as cur:
        cur.execute(existing_destination_query, {"destination_id": destination_id})
        existing_destination_data = cur.fetchone()
        if existing_destination_data is None:
            raise HTTPException(status_code=404, detail="Account not found")
        
    destination_update_data = {
        "destination_id": existing_destination_data.get("DESTINATION_ID"),
        "url": existing_destination_data.get("URL"),
        "http_method": existing_destination_data.get("HTTP_METHOD"),
        "headers": existing_destination_data.get("HEADERS"),
        "account_id": existing_destination_data.get("ACCOUNT_ID")
    }
    destination_data = destination.dict()
    headers_json = json.dumps(destination_data["headers"])
    updated_destination_data = destination_update_data.copy()
    updated_destination_data.update(destination.dict(exclude_unset=True))

    query = """
    UPDATE destinations
    SET url = %s, http_method = %s, headers = %s
    WHERE destination_id = %s
    """
    with conn.cursor() as cur:
        cur.execute(query, (updated_destination_data['url'], updated_destination_data['http_method'], headers_json, destination_id)) 
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Destination not found")
        return schemas.Destination(**updated_destination_data)


@router.delete("/destinations/{destination_id}/", response_model=schemas.Message)
def delete_destination(destination_id: int, conn=Depends(get_snowflake_conn)):
    """
    Delete a destination by ID
    """
    query = "DELETE FROM destinations WHERE destination_id = %(destination_id)s"
    with conn.cursor() as cur:
        cur.execute(query, {"destination_id": destination_id})
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Destination not found")
        return {"message": "Destination deleted successfully"}
