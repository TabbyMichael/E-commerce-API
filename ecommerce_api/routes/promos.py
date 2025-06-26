from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List

from ecommerce_api.models import PromoCode
from ecommerce_api.user_service import PromoCodeService, CartService
from ecommerce_api.exceptions import PromoCodeNotFound, InvalidPromoCode
from ecommerce_api.auth import get_current_admin_user, get_current_active_user

promo_code_service = PromoCodeService()
cart_service = CartService()

router = APIRouter()

@router.post("/", response_model=PromoCode, status_code=status.HTTP_201_CREATED)
async def create_promo_code(promo_code: PromoCode, current_user: dict = Depends(get_current_admin_user)):
    return await promo_code_service.create_promo_code(promo_code)

@router.get("/", response_model=List[PromoCode])
async def get_all_promo_codes(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_admin_user)
):
    return await promo_code_service.get_all_promo_codes(limit=limit, offset=offset)

@router.post("/apply-promo-code", response_model=dict)
async def apply_promo_code_to_cart(promo_code_str: str, current_user: dict = Depends(get_current_active_user)):
    try:
        cart = await cart_service.get_cart(current_user["user_id"])
        discount_amount = await promo_code_service.apply_promo_code_to_cart(cart, promo_code_str)
        return {"message": "Promo code applied successfully", "discount_amount": discount_amount}
    except (PromoCodeNotFound, InvalidPromoCode) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))