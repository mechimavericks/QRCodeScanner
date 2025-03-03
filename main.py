from fastapi import FastAPI,HTTPException,status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor import motor_asyncio
import os
from bson import ObjectId
app = FastAPI()


from dotenv import load_dotenv
load_dotenv()

mongourl = os.environ.get('MONGO_URI')

# Add this to the end of the file
try:
    client = motor_asyncio.AsyncIOMotorClient(mongourl)
    db = client["student"]
    collection = db["scannedqr"]
except Exception as e:
    print(e)
    exit(1)



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


@app.get("/")
async def get_scanned_data():
    try:
        localcollection = db["studentdata"]
        projection = {'_id': False}
        data = await localcollection.find({}, projection).to_list(length=None)
        return data
    except Exception as e:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))
    
@app.get("/get-data/{id}")
async def get_scanned_data(id: str):
    try:
        id = ObjectId(id)
        localcollection = db["studentdata"]
        data = await localcollection.find_one({"_id":id},projection={"_id":False})
        if not data:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Data not found")
        return data
    except Exception as e:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))
    


@app.post("/scan-qr/")
async def store_scanned_data(email: str):
    try:
        data = await collection.find_one({"email":email})
        if data:
            if data["status"]:
                return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="QR already Scanned")
            else:
                response = await collection.update_one({"email":email},{"$set":{"status":True}})
                if response.modified_count == 1:
                    return {"detail":"QR Scanned Successfully"}
                else:
                    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Failed to update data")
        else:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="QR is not Registered")
    except Exception as e:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))
    

@app.post("/insert-data/")
async def insert_data(data: InsertedData):
    try:
        # await collection.insert_one(data.dict())
        await collection.update_one({"email":data.email},{"$set":data.dict()},upsert=True)
        return {"detail":"Data stored successfully"}
    except Exception as e:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))