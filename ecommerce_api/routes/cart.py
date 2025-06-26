from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict

from ecommerce_api.models import Cart, CartItem
from ecommerce_api.user_service import CartService
from ecommerce_api.exceptions import ProductNotFound, CartNotFound
from ecommerce_api.auth import get_current_active_user

cart_service = CartService()

router = APIRouter()

@router.post("/items", response_model=Cart)
async def add_item_to_cart(item: CartItem, current_user: dict = Depends(get_current_active_user)):
    try:
        return await cart_service.add_item_to_cart(current_user["user_id"], item.product_id, item.quantity)
    except ProductNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.put("/items/{product_id}", response_model=Cart)
async def update_cart_item_quantity(product_id: str, quantity: Dict[str, int], current_user: dict = Depends(get_current_active_user)):
    try:
        return await cart_service.update_cart_item_quantity(current_user["user_id"], product_id, quantity["quantity"])
    except ProductNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/items/{product_id}", response_model=Cart)
async def remove_item_from_cart(product_id: str, current_user: dict = Depends(get_current_active_user)):
    try:
        return await cart_service.remove_item_from_cart(current_user["user_id"], product_id)
    except ProductNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/", response_model=Cart)
async def get_cart(current_user: dict = Depends(get_current_active_user)):
    return await cart_service.get_cart(current_user["user_id"])