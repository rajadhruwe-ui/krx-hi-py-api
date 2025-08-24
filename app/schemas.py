from pydantic import BaseModel, Field
from typing import List, Optional

class TranslateRequest(BaseModel):
    text: str = Field(..., description="Kurukh text to translate")
    debug: Optional[bool] = Field(default=False, description="Return debug info")

class TranslateResponse(BaseModel):
    translated_text: str
    debug: Optional[dict] = None

class BatchTranslateRequest(BaseModel):
    texts: List[str]
    debug: Optional[bool] = False

class BatchTranslateResponse(BaseModel):
    items: List[TranslateResponse]
