from typing import List
from app.schemas import CandidateProduct, RankedProduct


def score_product(
        candidate: CandidateProduct,
        context_category: str,
        context_brand: str | None,
        context_price: float, 
) -> float:
    score = 0.0

    if candidate.category == context_category:
        score += 0.45

    if context_brand and candidate.brand == context_brand:
        score += 0.20

    price_diff = abs(candidate.price - context_price)
    price_similarity = max(0, 1 - (price_diff / max(context_price, 1)))
    score += 0.20 * price_similarity

    score += 0.10 * float(candidate.popularity_score or 0)
    score += 0.05 * (float(candidate.rating or 0) / 5.0)

    return round(score, 4)


def rank_products(
        candidates: List[CandidateProduct],
        context_category: str,
        context_brand: str | None,
        context_price: float, 
) -> List[RankedProduct]:
    ranked = []

    for candidate in candidates:
        score = score_product(
            candidate=candidate,
            context_category=context_category,
            context_brand=context_brand,
            context_price=context_price,
        )

        ranked.append(
            RankedProduct(
                product_id=candidate.product_id,
                score=score,
            )
        )
    
    ranked.sort(key=lambda x: x.score, reverse = True)
    return ranked