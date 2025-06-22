import uuid
import logging
import pandas as pd
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import boto3

from backend.curGen import generate_focus_data
from backend.validate_cur import validate_focus_df
from backend.config import get_settings
from backend.logging_config import setup_logging
from backend.rate_limit_middleware import RateLimitMiddleware
from backend.models import GenerateCURRequest
from backend.multi_file_generator import MultiFileGenerator
from datetime import datetime

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
    """Generate FOCUS-compliant CUR data with multi-cloud and multi-month support."""
    
    try:
        # Parse request body
        body = await request.json()
        req = GenerateCURRequest(**body)
    except Exception as e:
        logger.error(f"Invalid request: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
    
    logger.info("Generate CUR request", extra={
        "profile": req.profile,
        "distribution": req.distribution,
        "row_count": req.row_count,
        "providers": req.providers,
        "multi_month": req.multi_month,
        "trend_options": req.trend_options
    })

    # Initialize multi-file generator
    multi_gen = MultiFileGenerator()
    
    try:
        if req.multi_month and req.trend_options:
            # Generate multi-month trend data
            files = multi_gen.generate_trend_files(
                providers=req.providers,
                profile=req.profile,
                distribution=req.distribution,
                row_count=req.row_count,
                trend_options=req.trend_options
            )
        else:
            # Generate single month multi-cloud data
            files = multi_gen.generate_multi_cloud_files(
                providers=req.providers,
                profile=req.profile,
                distribution=req.distribution,
                row_count=req.row_count
            )
        
        # Create ZIP package
        temp_dir = None
        if settings.environment == "development" and settings.s3_bucket_name == "local":
            import os
            temp_dir = os.path.join(os.path.dirname(__file__), "files")
            
        zip_filename = multi_gen.create_zip_package(
            files=files,
            trend_options=req.trend_options if req.multi_month else None,
            temp_dir=temp_dir
        )
        
        # Get file summary
        summary = multi_gen.get_file_summary(files)
        
        # Handle file storage
        logger.info(f"Environment: {settings.environment}, S3 Bucket: {settings.s3_bucket_name}")
        if settings.environment == "development" and settings.s3_bucket_name == "local":
            # Local development
            file_url = f"http://localhost:8000/files/{zip_filename}"
            logger.info(f"Successfully created ZIP package: {zip_filename}")
        else:
            # Production - upload ZIP to S3
            import os
            zip_path = os.path.join(temp_dir or "/tmp", zip_filename)
            
            with open(zip_path, 'rb') as f:
                zip_data = f.read()
            
            put_object_params = {
                'Bucket': settings.s3_bucket_name,
                'Key': zip_filename,
                'Body': zip_data,
                'ContentType': 'application/zip',
            }
            
            if settings.s3_public_read:
                put_object_params['ACL'] = 'public-read'
            
            s3_client.put_object(**put_object_params)
            
            # Generate pre-signed URL
            file_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': settings.s3_bucket_name, 'Key': zip_filename},
                ExpiresIn=3600
            )
            
            # Clean up local file
            os.remove(zip_path)
            logger.info(f"Successfully uploaded {zip_filename} to S3")

        # Return response with summary
        return {
            "message": f"FOCUS data generated successfully!",
            "downloadUrl": file_url,
            "fileSize": f"{len(files)} files",
            "generationTime": "2-3 seconds",
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Failed to generate FOCUS data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate FOCUS data: {str(e)}"
        )

@app.get("/files/{filename}/csv")
async def get_csv_from_zip(filename: str):
    """Extract and return the first CSV file from a ZIP archive."""
    if settings.environment == "development" and settings.s3_bucket_name == "local":
        import os
        import zipfile
        from fastapi.responses import Response
        
        file_path = os.path.join(os.path.dirname(__file__), "files", filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        if filename.endswith('.zip'):
            # Extract first CSV from ZIP
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                csv_files = [f for f in zip_file.namelist() if f.endswith('.csv')]
                if csv_files:
                    csv_content = zip_file.read(csv_files[0])
                    return Response(
                        content=csv_content,
                        media_type="text/csv",
                        headers={
                            "Content-Disposition": f"inline; filename={csv_files[0]}"
                        }
                    )
            raise HTTPException(status_code=404, detail="No CSV file found in ZIP")
        else:
            raise HTTPException(status_code=400, detail="File is not a ZIP archive")
    else:
        raise HTTPException(status_code=404, detail="Endpoint only available in development")

@app.get("/files/{filename}")
async def get_file(filename: str):
    if settings.environment == "development" and settings.s3_bucket_name == "local":
        # Local development - serve from files directory
        import os
        
        files_dir = os.path.join(os.path.dirname(__file__), "files")
        file_path = os.path.join(files_dir, filename)
        
        if os.path.exists(file_path):
            # Determine media type based on file extension
            media_type = 'application/zip' if filename.endswith('.zip') else 'text/csv'
            
            return FileResponse(
                path=file_path,
                filename=filename,
                media_type=media_type
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