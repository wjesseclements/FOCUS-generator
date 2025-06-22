import uuid
import logging
import pandas as pd
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime

from backend.curGen import generate_focus_data
from backend.validate_cur import validate_focus_df
from backend.config import get_settings
from backend.logging_config import setup_logging

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

# Add CORS middleware with secure configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0"
    }

@app.post("/generate-cur")
async def generate_cur(request: Request):
    """Generate FOCUS CUR data - simplified version."""
    
    try:
        # Parse request body
        body = await request.json()
        logger.info(f"Received request: {body}")
        
        profile = body.get("profile", "Greenfield")
        distribution = body.get("distribution", "Evenly Distributed")
        row_count = body.get("row_count", 20)
        providers = body.get("providers", ["aws"])
        
        # For now, just generate a simple CSV for single provider
        provider = providers[0] if providers else "aws"
        
        # Generate the data
        df = generate_focus_data(
            row_count=row_count,
            profile=profile,
            distribution=distribution,
            cloud_provider=provider.upper()
        )
        
        # Validate
        validate_focus_df(df)
        
        # Save to file
        files_dir = os.path.join(os.path.dirname(__file__), "files")
        os.makedirs(files_dir, exist_ok=True)
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{provider}-focus-{datetime.now().strftime('%Y-%m')}-{unique_id}.csv"
        file_path = os.path.join(files_dir, filename)
        
        df.to_csv(file_path, index=False)
        
        # Return response
        return {
            "message": "FOCUS data generated successfully!",
            "downloadUrl": f"http://localhost:8000/files/{filename}",
            "fileSize": f"{len(df)} rows",
            "generationTime": "1-2 seconds"
        }
        
    except Exception as e:
        logger.error(f"Error generating CUR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/{filename}")
async def get_file(filename: str):
    """Serve generated files."""
    files_dir = os.path.join(os.path.dirname(__file__), "files")
    file_path = os.path.join(files_dir, filename)
    
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='text/csv' if filename.endswith('.csv') else 'application/zip',
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    else:
        raise HTTPException(status_code=404, detail="File not found.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)