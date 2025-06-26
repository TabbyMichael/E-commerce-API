from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List

from ecommerce_api.models import Order
from ecommerce_api.user_service import OrderService
from ecommerce_api.exceptions import CartNotFound, OrderNotFound, InsufficientStock
from ecommerce_api.auth import get_current_active_user

order_service = OrderService()

router = APIRouter()

@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order_from_cart(current_user: dict = Depends(get_current_active_user)):
    try:
        return await order_service.create_order_from_cart(current_user["user_id"])
    except CartNotFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except InsufficientStock as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[Order])
async def get_all_orders(
    current_user: dict = Depends(get_current_active_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    return await order_service.get_all_orders(current_user["user_id"], limit=limit, offset=offset)

@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    try:
        return await order_service.get_order(current_user["user_id"], order_id)
    except OrderNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/pay/{order_id}", response_model=Order)
async def simulate_payment_success(
    order_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    try:
        return await order_service.update_order_status(current_user["user_id"], order_id, "paid")
    except OrderNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))