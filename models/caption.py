from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Caption(BaseModel):
    id: Optional[int] = None
    caption: str
    timestamp: Optional[datetime] = None
    image_base64: Optional[str] = None