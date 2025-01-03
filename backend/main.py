import os
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.post("/generate-cur")
async def generate_cur(request: Request):
    # Parse the JSON payload
    body = await request.json()
    row_count = body.get("row_count", 20)  # Default to 20 if not provided

    # Debugging: Log the received row_count
    print(f"Raw request body: {body}")
    print(f"Extracted row_count: {row_count}")

    # Ensure the row_count is parsed as an integer
    try:
        row_count = int(row_count)
        print(f"Parsed row_count: {row_count}")
    except ValueError:
        return {"message": "Invalid row_count. It must be an integer.", "url": None}

    # Generate dummy data for the CUR
    data = {
        "InvoiceId": [f"INV-{i+1}" for i in range(row_count)],
        "UsageAccountId": [f"123456789012" for _ in range(row_count)],
        "ProductName": ["Amazon EC2" for _ in range(row_count)],
        "UsageType": ["BoxUsage" for _ in range(row_count)],
        "BlendedCost": [round(i * 0.5, 2) for i in range(row_count)],
    }

    # Create a DataFrame
    df = pd.DataFrame(data)

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
    return FileResponse(filepath)