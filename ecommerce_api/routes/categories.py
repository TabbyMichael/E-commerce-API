from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List

from ecommerce_api.models import Category
from ecommerce_api.user_service import CategoryService
from ecommerce_api.exceptions import CategoryNotFound
from ecommerce_api.auth import get_current_admin_user

category_service = CategoryService()

router = APIRouter()

@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(category: Category, current_user: dict = Depends(get_current_admin_user)):
    return await category_service.create_category(category)

@router.get("/{category_id}", response_model=Category)
async def get_category(category_id: str):
    try:
        return await category_service.get_category(category_id)
    except CategoryNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/", response_model=List[Category])
async def get_all_categories(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    return await category_service.get_all_categories(limit=limit, offset=offset)

@router.put("/{category_id}", response_model=Category)
async def update_category(category_id: str, category: Category, current_user: dict = Depends(get_current_admin_user)):
    try:
        return await category_service.update_category(category_id, category.dict(exclude_unset=True))
    except CategoryNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: str, current_user: dict = Depends(get_current_admin_user)):
    try:
        await category_service.delete_category(category_id)
    except CategoryNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))