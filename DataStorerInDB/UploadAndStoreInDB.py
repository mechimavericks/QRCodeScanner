import os
import requests
from dotenv import load_dotenv
import pandas as pd
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables
load_dotenv()

# Configurations
API_KEY = os.getenv("API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
SHEET_PATH = "StudentData.xlsx"  # Change to "students.csv" if needed

print(API_KEY)
print(MONGO_URI)

# Connect to MongoDB 
try:
    client = AsyncIOMotorClient(MONGO_URI)
    db = client["student"]
    collection = db["studentdata"]
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit(1)

# Function to upload image to ImgBB
def upload_to_imgbb(image_path):
    try:
        with open(image_path, "rb") as img_file:
            response = requests.post(
                "https://api.imgbb.com/1/upload",
                data={"key": API_KEY},
                files={"image": img_file},
                timeout=30  # Added timeout
            )
            response.raise_for_status()

            if response.status_code == 200:
                return response.json()["data"]["url"]
            else:
                print(f"Upload failed for {image_path}: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"Error uploading {image_path} to ImgBB: {e}")
        return None

async def process_students():
    # Load Student Data from Local Sheet
    if SHEET_PATH.endswith(".xlsx"):
        df = pd.read_excel(SHEET_PATH)
    else:
        df = pd.read_csv(SHEET_PATH)
    print(df)
    
    try:
        for _, row in df.iterrows():
            fullname = row["Full Name"]
            email = row["Email Address"]
            rollno = row["Roll No"]
            address = row["Address"]

            compress_dir = "CompressedImages"
            filelocation = f"{compress_dir}/{rollno}_compressed.jpg"

            uplaodResponse = upload_to_imgbb(filelocation)
            if uplaodResponse is None:
                print(f"Failed to upload {filelocation}")
                continue
            
            # Insert student data into MongoDB
            dbresponse = await collection.insert_one({
                "fullname": fullname,
                "email": email,
                "rollno": rollno,
                "address": address,
                "imageurl": uplaodResponse,
                "status": False
            })
            print(f"Inserted document of {fullname} id: {dbresponse.inserted_id}")
    except Exception as e:
        print(f"Error processing student data: {e}")

if __name__ == "__main__":
    asyncio.run(process_students())
    print("Processing completed!")