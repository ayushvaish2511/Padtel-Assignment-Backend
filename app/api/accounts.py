from fastapi import APIRouter, Depends, HTTPException
from snowflake.connector import DictCursor

import secrets
import string

from app.models import account
from app.db import snowflake

router = APIRouter()

def get_snowflake_conn():
    return snowflake.connect_to_snowflake()

def generate_app_secret_token():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(32))  

@router.post("/accounts/", response_model=int)
def create_account(account: account.AccountCreate, conn=Depends(get_snowflake_conn)):
    """
    Create a new account
    """
    app_secret_token = generate_app_secret_token()  # Generate app_secret_token
    account_data = account.dict()
    account_data["app_secret_token"] = app_secret_token
    query = """
    INSERT INTO accounts (email, account_name, app_secret_token, website)
    VALUES (%(email)s, %(account_name)s, %(app_secret_token)s, %(website)s)
    """
    with conn.cursor() as cur:
        cur.execute(query, account_data)
        cur.execute("SELECT account_id FROM accounts WHERE email = %s AND account_name = %s", (account_data['email'], account_data['account_name']))
        row = cur.fetchone()
        return row[0]


@router.get("/accounts/{account_id}/", response_model=account.AccountReturn)
def get_account(account_id: int, conn=Depends(get_snowflake_conn)):
    """
    Get an account by ID
    """
    query = "SELECT * FROM accounts WHERE account_id = %(account_id)s"
    with conn.cursor(DictCursor) as cur:
        cur.execute(query, {"account_id": account_id})
        account_data = cur.fetchone()
        if account_data is None:
            raise HTTPException(status_code=404, detail="Account not found")

        print('returnnn', account_data)
        return account.AccountReturn(**account_data)


@router.put("/accounts/{account_id}/", response_model=account.Account)
def update_account(account_id: int, account: account.AccountUpdate, conn = Depends(get_snowflake_conn)):
    """
    Update an account by ID
    """
    existing_account_query = "SELECT * FROM accounts WHERE account_id = %(account_id)s"
    with conn.cursor(DictCursor) as cur:
        cur.execute(existing_account_query, {"account_id": account_id})
        existing_account_data = cur.fetchone()
        if existing_account_data is None:
            raise HTTPException(status_code=404, detail="Account not found")
    
    account_update_data = {
        "account_id": existing_account_data.get("ACCOUNT_ID"),
        "email": existing_account_data.get("EMAIL"),
        "account_name": existing_account_data.get("ACCOUNT_NAME"),
        "website": existing_account_data.get("WEBSITE"),
        "app_secret_token": existing_account_data.get("APP_SECRET_TOKEN")
    }

    updated_account_data = account_update_data.copy()
    updated_account_data.update(account.dict(exclude_unset=True))  
    print('updateee', updated_account_data)
    update_query = """
    UPDATE accounts
    SET email = %(email)s, account_name = %(account_name)s, website = %(website)s
    WHERE account_id = %(account_id)s
    """
    with conn.cursor() as cur:
        cur.execute(update_query, updated_account_data)
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Account not found")
        return account.Account(**updated_account_data)


@router.delete("/accounts/{account_id}/", response_model=account.Message)
def delete_account(account_id: int, conn = Depends(get_snowflake_conn)):
    """
    Delete an account by ID
    """
    query = "DELETE FROM accounts WHERE account_id = %(account_id)s"
    with conn.cursor() as cur:
        cur.execute(query, {"account_id": account_id})
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Account not found")
        return {"message": "Account deleted successfully"}

