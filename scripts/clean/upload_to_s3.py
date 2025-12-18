from dotenv import load_dotenv
load_dotenv()

import boto3
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[2]
FILE_PATH = BASE_DIR / "data" / "indemnizatii_clean.csv"

BUCKET = os.environ["S3_ARTIFACTS_BUCKET"]
KEY = "indemnizatii/indemnizatii_clean.csv"

def main():
    if not FILE_PATH.exists():
        raise FileNotFoundError(f"File not found: {FILE_PATH}")
    
    s3 = boto3.client("s3")
    s3.upload_file(
        Filename=str(FILE_PATH),
        Bucket=BUCKET,
        Key=KEY
    )

    print(f"File uploaded to s3://{BUCKET}/{KEY}")

if __name__ == "__main__":
    main()