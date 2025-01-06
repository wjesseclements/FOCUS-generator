import os
import pandas as pd
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from curGen import generate_focus_data  # Import the function from curGen.py

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Predefined profiles and distributions
VALID_PROFILES = ["Greenfield", "Large Business", "Enterprise"]
VALID_DISTRIBUTIONS = ["Evenly Distributed", "ML-Focused", "Data-Intensive", "Media-Intensive"]

@app.post("/generate-cur")
async def generate_cur(request: Request):
    # Parse incoming request body
    body = await request.json()

    # Log the raw request body (for debugging)
    print(f"Raw request body: {body}")

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

    # Generate CUR data using curGen.py
    df = generate_focus_data(row_count=row_count, distribution=distribution, profile=profile)

    # Save the file locally
    filename = f"generated_CUR_{row_count}.csv"
    filepath = os.path.join("files", filename)
    os.makedirs("files", exist_ok=True)
    df.to_csv(filepath, index=False)

    # Construct the absolute URL
    base_url = request.base_url
    file_url = f"{base_url}files/{filename}"

    # Return the file URL
    return {"message": f"FOCUS-conformed CUR with {row_count} rows generated!", "url": file_url}


# Serve static files
@app.get("/files/{filename}")
async def get_file(filename: str):
    filepath = os.path.join("files", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(filepath)