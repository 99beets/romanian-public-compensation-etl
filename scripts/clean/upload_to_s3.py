# Upload cleaned dataset to S3 as a stable ingestion artifact.

from dotenv import load_dotenv
load_dotenv()   # Load environment variables from .env for local development

import boto3
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[2]
FILE_PATH = BASE_DIR / "data" / "indemnizatii_clean.csv"

BUCKET = os.environ["S3_ARTIFACTS_BUCKET"]
if not BUCKET:
    raise RuntimeError("S3_ARTIFACTS_BUCKET environments variable is not set")

KEY = "indemnizatii/indemnizatii_clean.csv"

def main():
    # Ensure cleaned dataset exists before attempting upload
    if not FILE_PATH.exists():
        raise FileNotFoundError(f"File not found: {FILE_PATH}")
    
    # Create S3 client using configured AWS credentials (env/profile)
    s3 = boto3.client("s3")

    # Upload file as a versionable artifact for downstream consumption
    s3.upload_file(
        Filename=str(FILE_PATH),
        Bucket=BUCKET,
        Key=KEY
    )

    print(f"File uploaded to s3://{BUCKET}/{KEY}")

if __name__ == "__main__":
    main()