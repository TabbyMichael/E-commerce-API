from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from ecommerce_api.models import Product
from ecommerce_api.user_service import ProductService
from ecommerce_api.exceptions import ProductNotFound
from ecommerce_api.auth import get_current_admin_user # Assuming only admin can CRUD products

product_service = ProductService()

router = APIRouter()

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(product: Product, current_user: dict = Depends(get_current_admin_user)):
    return await product_service.create_product(product)

@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    try:
        return await product_service.get_product(product_id)
    except ProductNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/", response_model=List[Product])
async def get_all_products(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category_id: Optional[str] = Query(None),
    in_stock: Optional[bool] = Query(None)
):
    return await product_service.get_all_products(limit=limit, offset=offset, category_id=category_id, in_stock=in_stock)

@router.put("/{product_id}", response_model=Product)
async def update_product(product_id: str, product: Product, current_user: dict = Depends(get_current_admin_user)):
    try:
        return await product_service.update_product(product_id, product.dict(exclude_unset=True))
    except ProductNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str, current_user: dict = Depends(get_current_admin_user)):
    try:
        await product_service.delete_product(product_id)
    except ProductNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/search", response_model=List[Product])
async def search_products(
    q: str = Query(..., min_length=1, description="Search keyword for product name or description"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    return await product_service.search_products(q, limit=limit, offset=offset)