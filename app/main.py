from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.accounts import router as accounts_router
from app.api.destinations import router as destinations_router
from app.api.data_handler import router as data_handler_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity, replace with your frontend URL in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Include OPTIONS method
    allow_headers=["*"],
)

app.include_router(accounts_router, tags=['Account'])
app.include_router(destinations_router, tags=['Destination'])
app.include_router(data_handler_router, tags=['DataHandling'])
# app.include_router(destinations.router)
# app.include_router(data_handler.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)