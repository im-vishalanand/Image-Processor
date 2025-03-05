# --- request.py (Pydantic Request Schemas) ---
from pydantic import BaseModel

class UploadRequest(BaseModel):
    file_name: str  # Just an example; can be expanded later
