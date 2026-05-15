from pydantic import BaseModel, ConfigDict
from typing import Optional

class Token(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    access_token: str
    token_type: str

class TokenData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    user_id: Optional[int] = None