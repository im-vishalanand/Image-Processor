# --- response.py (Pydantic Response Schemas) ---
from pydantic import BaseModel
from typing import List, Optional

class ImageResponse(BaseModel):
    input: str
    output: Optional[str]  # Can be "processing" if not yet completed

class StatusResponse(BaseModel):
    request_id: str
    status: str
    images: List[ImageResponse]
