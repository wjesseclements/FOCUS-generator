import uuid
import logging
import pandas as pd
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import boto3

from .curGen import generate_focus_data
from .validate_cur import validate_focus_df
from .config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize settings
settings = get_settings()

app = FastAPI(
    title="FOCUS CUR Generator API",
    description="Generate synthetic FOCUS-compliant Cost and Usage Reports",
    version="1.0.0",
    debug=settings.debug
)

# Add CORS middleware with secure configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST"],  # Only allow specific methods
    allow_headers=["Content-Type", "Authorization"],  # Only allow specific headers
)

# S3 client
s3_client = boto3.client('s3')

# Predefined profiles and distributions
VALID_PROFILES = ["Greenfield", "Large Business", "Enterprise"]
VALID_DISTRIBUTIONS = ["Evenly Distributed", "ML-Focused", "Data-Intensive", "Media-Intensive"]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "FOCUS CUR Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


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

    # Log received data
    logger.info(f"Generate CUR request - Profile: {profile}, Distribution: {distribution}, Rows: {row_count}")

    # 1. Generate the CUR data
    df = generate_focus_data(row_count=row_count, profile=profile, distribution=distribution)

    # 2. Validate the generated DataFrame
    try:
        validate_focus_df(df)
        logger.info(f"Data validation passed for {row_count} rows")
    except ValueError as e:
        logger.error(f"Data validation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Data validation failed: {str(e)}"
        )

    # 3. Save to CSV in memory
    filename = f"generated_CUR_{row_count}_{uuid.uuid4().hex[:8]}.csv"
    csv_data = df.to_csv(index=False)
    
    # 4. Upload to S3
    try:
        # Upload without public ACL for better security
        put_object_params = {
            'Bucket': settings.s3_bucket_name,
            'Key': filename,
            'Body': csv_data,
            'ContentType': 'text/csv',
        }
        
        # Only add public ACL if explicitly configured (not recommended for production)
        if settings.s3_public_read:
            put_object_params['ACL'] = 'public-read'
        
        s3_client.put_object(**put_object_params)
        
        # Generate a pre-signed URL (valid for 1 hour)
        file_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.s3_bucket_name, 'Key': filename},
            ExpiresIn=3600
        )
        logger.info(f"Successfully uploaded {filename} to S3 bucket {settings.s3_bucket_name}")
    except Exception as e:
        logger.error(f"Failed to upload file to S3: {str(e)}")
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
            Params={'Bucket': settings.s3_bucket_name, 'Key': filename},
            ExpiresIn=3600
        )
        return RedirectResponse(url=file_url)
    except Exception:
        raise HTTPException(status_code=404, detail="File not found.")