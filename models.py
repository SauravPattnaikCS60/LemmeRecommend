from pydantic import BaseModel
from typing import List

class Response(BaseModel):
    features : List[str]
    search_query : str