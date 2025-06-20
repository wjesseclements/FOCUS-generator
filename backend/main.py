import uuid
import logging
import pandas as pd
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import boto3

from backend.curGen import generate_focus_data
from backend.validate_cur import validate_focus_df
from backend.config import get_settings
from backend.logging_config import setup_logging
from backend.rate_limit_middleware import RateLimitMiddleware

# Configure logging
logger = setup_logging(__name__)

# Initialize settings
settings = get_settings()

app = FastAPI(
    title="FOCUS CUR Generator API",
    description="Generate synthetic FOCUS-compliant Cost and Usage Reports",
    version="1.0.0",
    debug=settings.debug
)

# Add rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    requests_per_hour=100,
    requests_per_minute=10
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
    
    # 4. Handle file storage (S3 for production, local for development)
    if settings.environment == "development" and settings.s3_bucket_name == "local":
        # Local development - save to files directory
        import os
        files_dir = os.path.join(os.path.dirname(__file__), "files")
        os.makedirs(files_dir, exist_ok=True)
        file_path = os.path.join(files_dir, filename)
        
        with open(file_path, 'w') as f:
            f.write(csv_data)
        
        # Return local file URL pointing to backend
        file_url = f"http://localhost:8000/files/{filename}"
        logger.info(f"Successfully saved {filename} to local files directory")
    else:
        # Production - upload to S3
        try:
            put_object_params = {
                'Bucket': settings.s3_bucket_name,
                'Key': filename,
                'Body': csv_data,
                'ContentType': 'text/csv',
            }
            
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
    if settings.environment == "development" and settings.s3_bucket_name == "local":
        # Local development - serve from files directory
        import os
        from fastapi.responses import FileResponse
        
        files_dir = os.path.join(os.path.dirname(__file__), "files")
        file_path = os.path.join(files_dir, filename)
        
        if os.path.exists(file_path):
            return FileResponse(
                path=file_path,
                filename=filename,
                media_type='text/csv'
            )
        else:
            raise HTTPException(status_code=404, detail="File not found.")
    else:
        # Production - redirect to S3
        try:
            file_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': settings.s3_bucket_name, 'Key': filename},
                ExpiresIn=3600
            )
            return RedirectResponse(url=file_url)
        except Exception:
            raise HTTPException(status_code=404, detail="File not found.")