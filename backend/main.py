import os
import uuid
import pandas as pd
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import boto3

from .curGen import generate_focus_data
from .validate_cur import validate_focus_df

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# S3 client
s3_client = boto3.client('s3')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'cur-gen-files')  # Set this in Lambda environment variables

# Predefined profiles and distributions
VALID_PROFILES = ["Greenfield", "Large Business", "Enterprise"]
VALID_DISTRIBUTIONS = ["Evenly Distributed", "ML-Focused", "Data-Intensive", "Media-Intensive"]

@app.post("/generate-cur")
async def generate_cur(request: Request):
    # Parse incoming request body
    body = await request.json()
    profile = body.get("profile", "").strip()
    distribution = body.get("distribution", "").strip()
    row_count = body.get("row_count", 20)

    # Validate inputs
    if profile not in VALID_PROFILES:
        raise HTTPException(status_code=400, detail="Invalid profile selected.")
    if distribution not in VALID_DISTRIBUTIONS:
        raise HTTPException(status_code=400, detail="Invalid distribution selected.")
    try:
        row_count = int(row_count)
    except ValueError:
        raise HTTPException(status_code=400, detail="row_count must be an integer.")

    # Log received data (for debugging)
    print(f"Received profile: {profile}")
    print(f"Received distribution: {distribution}")
    print(f"Received row_count: {row_count}")

    # 1. Generate the CUR data
    df = generate_focus_data(row_count=row_count, profile=profile, distribution=distribution)

    # 2. Validate the generated DataFrame
    try:
        validate_focus_df(df)
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Data validation failed: {str(e)}"
        )

    # 3. Save to CSV in memory
    filename = f"generated_CUR_{row_count}_{uuid.uuid4().hex[:8]}.csv"
    csv_data = df.to_csv(index=False)
    
    # 4. Upload to S3
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=filename,
            Body=csv_data,
            ContentType='text/csv',
            ACL='public-read'  # Make it publicly accessible
        )
        
        # Generate a pre-signed URL (valid for 1 hour)
        file_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': filename},
            ExpiresIn=3600
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file to S3: {str(e)}"
        )

    # 5. Return success with the file URL
    return {
        "message": f"FOCUS-conformed CUR with {row_count} rows generated and validated!",
        "url": file_url
    }

@app.get("/files/{filename}")
async def get_file(filename: str):
    # For compatibility with old code, redirect to S3
    try:
        file_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': filename},
            ExpiresIn=3600
        )
        return RedirectResponse(url=file_url)
    except Exception:
        raise HTTPException(status_code=404, detail="File not found.")