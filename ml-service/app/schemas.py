from pydantic import BaseModel
from typing import List, Optional

class CandidateProduct(BaseModel):
    product_id: str
    name: str
    category: str
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    price = float
    rating: Optional[float] = 0.0
    popularity_score: Optional[float] = 0.0

class RankRequest(BaseModel):
    user_id: str
    context_product_id: str
    context_category: str
    context_brand: Optional[str] = None
    context_pice: float
    candidate_products: List[CandidateProduct]

class RankedProduct(BaseModel):
    product_id: str
    score: float

class RankResponse(BaseModel):
    user_id: str
    ranked_products: List[RankedProduct]
