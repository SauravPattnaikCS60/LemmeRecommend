from pydantic import BaseModel
from typing import List

class Response(BaseModel):
    features : List[str]
    rationale : str
    search_query : str