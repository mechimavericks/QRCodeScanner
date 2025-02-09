import os
import requests
import pandas as pd

# Configurations
SHEET_PATH = "student.xlsx"  # Change to "students.csv" if CSV file
API_KEY= "0325dca8c62672d74a4bf4682e01e739"

# Load Student Data from Local Sheet
df = pd.read_excel(SHEET_PATH) if SHEET_PATH.endswith(".xlsx") else pd.read_csv(SHEET_PATH)
print(df)

# Ensure expected columns exist
if "Email Address" not in df.columns or "Student Photo" not in df.columns:
    raise ValueError("Sheet must contain 'Email Address' and 'Student Photo' columns.")

# Function to download image
def download_image(image_url, save_path):
    # Modify Google Drive URL to directly download the image
    if "drive.google.com" in image_url:
        file_id = image_url.split("id=")[-1]
        image_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    try:
        response = requests.get(image_url, stream=True, timeout=10)  # Added timeout
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        with open(save_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return save_path
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {image_url}: {e}")
        return None

# Function to upload image to ImgBB
def upload_to_imgbb(image_path):
    try:
        with open(image_path, "rb") as img_file:
            response = requests.post(
                "https://api.imgbb.com/1/upload",
                data={"key": API_KEY},
                files={"image": img_file},
                timeout=10 # Added timeout
            )
            response.raise_for_status()

            if response.status_code == 200:
                print(response.json())
                return response.json()["data"]["url"]
            else:
                print(f"Upload failed for {image_path}: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"Error uploading {image_path} to ImgBB: {e}")
        return None

# Process Each Student
if SHEET_PATH.endswith(".xlsx"):
    row = df.iloc[0]
    email = row["Email Address"]
    image_url = row["Student Photo"]

    local_path = f"images/{email}.jpg"
    os.makedirs("images", exist_ok=True)

    # Download and upload image
    res = download_image(image_url, local_path)
    if res:
        img_url = upload_to_imgbb(res)
        print(f"Uploaded {img_url} for {email}")

print("Processing completed!")
