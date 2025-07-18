from mangum import Mangum
from main import app  # Changed from backend.main

handler = Mangum(app)