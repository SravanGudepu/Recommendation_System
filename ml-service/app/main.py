from fastapi import FastAPI
from app.schemas import RankRequest, RankResponse
from app.inference import rank_products

app = FastAPI(title="ML Recommendation Inference Service")

@app.get("/health")
def health():
    return {"status": "ok", "service": "ml-inference"}

@app.post("/rank", response_model=RankResponse)
def rank(request: RankRequest):
    ranked_products = rank_products(
        candidates=request.candidate_products,
        context_category=request.context_category,
        context_brand=request.context_brand,
        context_price=request.context_price,
    )

    return RankResponse(
        user_id=request.user_id,
        ranked_products=ranked_products,
    )