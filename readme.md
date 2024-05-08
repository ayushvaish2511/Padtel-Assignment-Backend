# Data Pusher

This project provides a FastAPI web application to receive data into the app server for an account and send it across different platforms (destinations) from that particular account using webhook URLs. 

This project uses FastAPI and Snowflake Database.

## Sample APIs

### Accounts Management
#### Create new Account
- Method: POST
- Endpoint: `/accounts/`
- Description: Create a new account.

#### Get Account
- Method: GET
- Endpoint: `/accounts/{account_id}/`
- Description: Get account details by ID.

#### Update Account

- Method: PUT
- Endpoint: `/accounts/{account_id}/`
- Description: Update account details by ID.

#### Delete Account
- Method: DELETE
- Endpoint: `/accounts/{account_id}/`
- Description: Delete an account by ID.

### Destination Management
#### Create Destination
- Method: POST
- Endpoint: `/destinations/`
- Description: Create a new destination.

#### Get Destination
- Method: GET
- Endpoint: `/destinations/{destination_id}/`
- Description: Get destination details by ID.

#### Update Destination
- Method: PUT
- Endpoint: `/destinations/{destination_id}/`
- Description: CrUpdate destination details by ID.

#### Delete Destination
- Method: DELETE
- Endpoint: `/destinations/{destination_id}/`
- Description: Delete a destination by ID.

### Data Handling
- Method: POST
- Endpoint: `/server/incoming_data`
#### Description: 
- Receive incoming data and send it to the specified destinations.
- Validates the incoming data to ensure it is in JSON format.
- Requires an app secret token to authenticate the request.
- Identifies the account associated with the provided secret token.
- Sends the received data to the destinations associated with the identified account.

## Installation

1. Clone the repository:

```git clone https://github.com/ayushvaish2511/Padtel-Assignment-Backend.git```

2. Navigate to the project directory:

```cd Padtel-Assignment-Backend```

3. Create Virtual Environment:

```python -m venv backennd-venv```

4. Install the dependencies:

```pip install -r requirements.txt```


## Running the Application

1. Start the FastAPI server:

```uvicorn app.main:app --reload```

This will start the server at `http://localhost:8000` by default.

2. You can now access the API documentation using your browser or API client:

`http://localhost:8000/docs`




