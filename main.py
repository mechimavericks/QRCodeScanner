from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor import motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InsertedData(BaseModel):
    name: str
    email: str
    rollno: str
    status: bool = False

# Initialize MongoDB client
client = motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI"))
db = client["student"]
collection = db["scannedqr"]

@app.get("/")
async def get_scanned_data():
    try:
        data = await collection.find().to_list(length=None)
        return data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/scan-qr/")
async def store_scanned_data(email: str):
    try:
        data = await collection.find_one({"email": email})
        if data:
            if data["status"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="QR already Scanned")
            else:
                response = await collection.update_one({"email": email}, {"$set": {"status": True}})
                if response.modified_count == 1:
                    return {"detail": "QR Scanned Successfully"}
                else:
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update data")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR Is not Registered")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/insert-data/")
async def insert_data(data: InsertedData):
    try:
        await collection.update_one({"email": data.email}, {"$set": data.dict()}, upsert=True)
        return {"detail": "Data stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
