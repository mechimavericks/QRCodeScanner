import os
import requests
import pandas as pd
from PIL import Image

# Configurations
SHEET_PATH = "StudentData.xlsx"  # Change to "students.csv" if CSV file

# Load Student Data from Local Sheet



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

# Function to compress image using Pillow
def compress_image(input_path, output_path, quality=70):
    try:
        image = Image.open(input_path)
        image.save(output_path, "JPEG", optimize=True, quality=quality)
        return output_path
    except Exception as e:
        print(f"Error compressing image {input_path}: {e}")
        return None

if __name__ == "__main__":
    # Process Each Student
    if SHEET_PATH.endswith(".xlsx"):
        df = pd.read_excel(SHEET_PATH) if SHEET_PATH.endswith(".xlsx") else pd.read_csv(SHEET_PATH)
        print(df)
        try:
            for _,row in df.iterrows():
                if "Email Address" not in df.columns or "Student Photo" not in df.columns:
                    print(f"Sheet must contain {row['Student Photo']} and 'Student Photo' columns.")
                    continue
                email = row["Email Address"]
                image_url = row["Student Photo"]
                rollno = row["Roll No"]

                download_dir = "DownloadImages"
                compress_dir = "CompressedImages"
                os.makedirs(download_dir, exist_ok=True)
                os.makedirs(compress_dir, exist_ok=True)

                local_path = f"{download_dir}/{rollno}.jpg"
                compressed_path = f"{compress_dir}/{rollno}_compressed.jpg"

                downloaded_image = download_image(image_url, local_path)
                if downloaded_image:
                    result_path = compress_image(downloaded_image, compressed_path)
                    if result_path:
                        print(f"Compressed image of {row['Full Name']} saved to {result_path}")
                    else:
                        print("Compression failed.")
                else:
                    print(f"Download failed for {row['Full Name']}")
        except Exception as e:
            print(f"Error processing student data: {e}")
            
    print("Processing completed!")