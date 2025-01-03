from fastapi import FastAPI
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
async def generate_cur(row_count: int = 20):
    return {
        "message": f"FOCUS-conformed CUR with {row_count} rows generated!",
        "url": f"/path/to/cur-file-{row_count}.csv"
    }