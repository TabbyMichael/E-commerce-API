from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Product(BaseModel):
    product_id: str
    name: str
    description: Optional[str] = None
    price: float
    stock_quantity: int
    SKU: str
    image_urls: List[str] = []
    is_active: bool = True
    category_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Category(BaseModel):
    category_id: str
    name: str
    description: Optional[str] = None
    parent_category_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class CartItem(BaseModel):
    product_id: str
    quantity: int
    price_at_addition: float

class Cart(BaseModel):
    user_id: str
    items: List[CartItem] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class OrderItem(BaseModel):
    product_id: str
    quantity: int
    price_at_purchase: float

class Order(BaseModel):
    order_id: str
    user_id: str
    total_amount: float
    status: str = "pending"
    order_items: List[OrderItem]
    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Review(BaseModel):
    review_id: str
    product_id: str
    user_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    is_approved: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class PromoCode(BaseModel):
    promo_code_id: str
    code: str
    discount_percentage: float = Field(..., ge=0, le=100)
    expiry_date: datetime
    usage_limit: Optional[int] = None
    times_used: int = 0
    applicable_products: List[str] = []
    applicable_categories: List[str] = []
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class User(BaseModel):
    user_id: str
    email: str
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None