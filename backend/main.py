import os
import pandas as pd
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .curGen import generate_focus_data  # Import the function from curGen.py
from .validate_cur import validate_focus_df  # Import your validator function

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    #    If it fails, raise an HTTPException for the pipeline or user to see
    try:
        validate_focus_df(df)
    except ValueError as e:
        # Validation failed; raise HTTP 500 or 422 depending on your preference
        raise HTTPException(
            status_code=500,
            detail=f"Data validation failed: {str(e)}"
        )

    # 3. If validation passes, save the file
    filename = f"generated_CUR_{row_count}.csv"
    filepath = os.path.join("files", filename)
    os.makedirs("files", exist_ok=True)
    df.to_csv(filepath, index=False)

    # 4. Construct the absolute URL for the file
    base_url = request.base_url
    file_url = f"{base_url}files/{filename}"

    # Return success with the file URL
    return {
        "message": f"FOCUS-conformed CUR with {row_count} rows generated and validated!",
        "url": file_url
    }

@app.get("/files/{filename}")
async def get_file(filename: str):
    filepath = os.path.join("files", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(filepath)