import uuid
import logging
import pandas as pd
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import boto3

from .curGen import generate_focus_data
from .validate_cur import validate_focus_df
from .config import get_settings
from .logging_config import setup_logging
from .redis_rate_limiter import EnhancedRateLimitMiddleware
from .csrf_protection import CSRFMiddleware
from .models import GenerateCURRequest
from .multi_file_generator import MultiFileGenerator
from .streaming_csv import (
    StreamingDataGenerator, 
    StreamingConfig, 
    streaming_csv_response,
    create_data_generator,
    estimate_csv_size
)
from .error_handler import ErrorHandler, ErrorContext, handle_errors
from .exceptions import (
    ValidationError, DataGenerationError, FileOperationError, 
    ExternalServiceError, ResourceLimitError
)
from .retry_utils import retry_with_backoff, EXTERNAL_SERVICE_RETRY, FILE_OPERATION_RETRY
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

# Add compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add CSRF protection middleware
if settings.is_production:
    app.add_middleware(
        CSRFMiddleware,
        secret_key=settings.csrf_secret_key,
        token_lifetime=3600,
        exempt_paths=["/health", "/docs", "/openapi.json", "/favicon.ico"]
    )

# Add enhanced rate limiting middleware
app.add_middleware(
    EnhancedRateLimitMiddleware,
    requests_per_minute=settings.rate_limit_per_minute,
    requests_per_hour=settings.rate_limit_per_hour,
    requests_per_day=settings.rate_limit_per_day
)

# Add CORS middleware with secure configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "OPTIONS"],  # Include OPTIONS for preflight
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-CSRF-Token"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset", "X-CSRF-Token"]
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
    
    with ErrorContext("generate_cur", {"endpoint": "/generate-cur"}):
        try:
            # Parse request body
            body = await request.json()
            req = GenerateCURRequest(**body)
        except Exception as e:
            raise ValidationError(
                "Invalid request body",
                details={"request_body": str(e)}
            )
        
        # Validate row count limits
        if req.row_count > settings.max_generation_timeout:
            raise ResourceLimitError(
                "Row count exceeds maximum limit",
                resource_type="row_count",
                current_value=req.row_count,
                limit_value=settings.max_generation_timeout
            )
        
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
                upload_result = upload_to_s3_with_retry(
                    zip_filename, temp_dir, settings.s3_bucket_name, settings.s3_public_read
                )
                file_url = upload_result
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
            if isinstance(e, (ValidationError, DataGenerationError, FileOperationError, 
                            ExternalServiceError, ResourceLimitError)):
                raise e
            else:
                raise DataGenerationError(
                    "Failed to generate FOCUS data",
                    operation="generate_cur",
                    parameters={
                        "profile": req.profile,
                        "distribution": req.distribution,
                        "row_count": req.row_count,
                        "providers": req.providers
                    },
                    details={"original_error": str(e)}
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


@app.post("/generate-cur-stream")
async def generate_cur_stream(request: Request, background_tasks: BackgroundTasks):
    """Generate and stream FOCUS-compliant CUR data for large datasets."""
    
    try:
        # Parse request body
        body = await request.json()
        req = GenerateCURRequest(**body)
    except Exception as e:
        logger.error(f"Invalid request: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
    
    # Check if request is suitable for streaming (large row count)
    if req.row_count < 10000:
        raise HTTPException(
            status_code=400, 
            detail="Use /generate-cur endpoint for small datasets (< 10,000 rows)"
        )
    
    logger.info("Generate CUR stream request", extra={
        "profile": req.profile,
        "distribution": req.distribution,
        "row_count": req.row_count,
        "providers": req.providers,
        "estimated_size_mb": estimate_csv_size(req.row_count, 50) / (1024 * 1024)
    })
    
    try:
        # Generate data using streaming approach
        streaming_config = StreamingConfig(
            chunk_size=5000,
            use_compression=True,
            temp_dir=None  # Use system temp dir
        )
        
        # For single-provider, single-month generation
        if not req.multi_month and len(req.providers) == 1:
            # Generate streaming data
            df = generate_focus_data(
                profile=req.profile,
                distribution=req.distribution,
                row_count=req.row_count,
                cloud_provider=req.providers[0].upper()
            )
            
            # Create streaming generator
            streaming_generator = StreamingDataGenerator(streaming_config)
            data_gen = create_data_generator(df, chunk_size=streaming_config.chunk_size)
            
            # Generate streaming CSV
            csv_writer = streaming_generator.generate_streaming_csv(
                data_generator=data_gen,
                headers=df.columns.tolist(),
                total_rows=req.row_count
            )
            
            # Stream the response
            filename = f"focus_data_{req.providers[0]}_{req.row_count}rows.csv.gz"
            
            with streaming_csv_response(
                csv_writer.get_temp_file_path(),
                filename=filename,
                cleanup=True
            ) as response:
                return response
                
        else:
            # For multi-provider or multi-month, fall back to regular generation
            raise HTTPException(
                status_code=400,
                detail="Streaming only supported for single-provider, single-month generation"
            )
            
    except Exception as e:
        logger.error(f"Failed to generate streaming CUR data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate streaming CUR data: {str(e)}"
        )


# Helper functions with retry logic
@retry_with_backoff(EXTERNAL_SERVICE_RETRY, "s3_upload")
def upload_to_s3_with_retry(zip_filename: str, temp_dir: str, bucket_name: str, public_read: bool) -> str:
    """Upload file to S3 with retry logic."""
    import os
    
    zip_path = os.path.join(temp_dir or "/tmp", zip_filename)
    
    try:
        with open(zip_path, 'rb') as f:
            zip_data = f.read()
        
        put_object_params = {
            'Bucket': bucket_name,
            'Key': zip_filename,
            'Body': zip_data,
            'ContentType': 'application/zip',
        }
        
        if public_read:
            put_object_params['ACL'] = 'public-read'
        
        s3_client.put_object(**put_object_params)
        
        # Generate pre-signed URL
        file_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': zip_filename},
            ExpiresIn=3600
        )
        
        # Clean up local file
        os.remove(zip_path)
        
        return file_url
        
    except Exception as e:
        raise ExternalServiceError(
            f"Failed to upload {zip_filename} to S3",
            service_name="s3",
            operation="put_object",
            details={"bucket": bucket_name, "key": zip_filename, "error": str(e)}
        )


# Global error handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions."""
    return ErrorHandler.handle_error_response(
        exc, 
        context={
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers)
        }
    )


# Custom error handlers for specific exception types
@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle validation errors."""
    return ErrorHandler.handle_error_response(exc)


@app.exception_handler(DataGenerationError)
async def data_generation_error_handler(request: Request, exc: DataGenerationError):
    """Handle data generation errors."""
    return ErrorHandler.handle_error_response(exc)


@app.exception_handler(FileOperationError)
async def file_operation_error_handler(request: Request, exc: FileOperationError):
    """Handle file operation errors."""
    return ErrorHandler.handle_error_response(exc)


@app.exception_handler(ExternalServiceError)
async def external_service_error_handler(request: Request, exc: ExternalServiceError):
    """Handle external service errors."""
    return ErrorHandler.handle_error_response(exc)


@app.exception_handler(ResourceLimitError)
async def resource_limit_error_handler(request: Request, exc: ResourceLimitError):
    """Handle resource limit errors."""
    return ErrorHandler.handle_error_response(exc)