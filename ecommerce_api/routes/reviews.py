from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from ecommerce_api.models import Review
from ecommerce_api.user_service import ReviewService
from ecommerce_api.exceptions import ProductNotFound, ReviewNotFound
from ecommerce_api.auth import get_current_active_user

review_service = ReviewService()

router = APIRouter()

@router.post("/{product_id}/reviews", response_model=Review, status_code=status.HTTP_201_CREATED)
async def create_product_review(
    product_id: str,
    rating: int,
    comment: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    try:
        return await review_service.create_review(product_id, current_user["user_id"], rating, comment)
    except ProductNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{product_id}/reviews", response_model=List[Review])
async def get_product_reviews(
    product_id: str,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    return await review_service.get_reviews_for_product(product_id, limit=limit, offset=offset)

@router.get("/{product_id}/reviews/average_rating", response_model=float)
async def get_product_average_rating(product_id: str):
    return await review_service.calculate_average_rating(product_id)