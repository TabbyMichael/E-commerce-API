from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta


import uuid

from ecommerce_api.firestore import db
from ecommerce_api.models import (
    Product, Category, CartItem, Cart, OrderItem, Order, Review, PromoCode, User
)
from ecommerce_api.exceptions import (
    ProductNotFound, CategoryNotFound, CartNotFound, OrderNotFound, 
    ReviewNotFound, PromoCodeNotFound, InvalidPromoCode, InsufficientStock,
    UserNotFound
)

APP_ID = "ecommerce_app"

class UserService:
    def __init__(self):
        self.collection_path = f"/artifacts/{APP_ID}/users"

    async def register_user(self, email: str, password_hash: str) -> User:
        user_id = str(uuid.uuid4())
        user_data = {
            "user_id": user_id,
            "email": email,
            "password_hash": password_hash,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        await db.add_document(self.collection_path, user_data)
        return User(**user_data)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        users = await db.query_collection(self.collection_path, filters={"email": email})
        if users:
            return User(**users[0])
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        user_data = await db.get_document(self.collection_path, user_id)
        if user_data:
            return User(**user_data)
        return None

    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> User:
        updated_data = await db.update_document(self.collection_path, user_id, user_data)
        if not updated_data:
            raise UserNotFound(f"User with ID {user_id} not found")
        return User(**updated_data)

class ProductService:
    def __init__(self):
        self.collection_path = f"/artifacts/{APP_ID}/public/data/products"

    async def create_product(self, product: Product) -> Product:
        product_data = product.dict()
        product_data["product_id"] = str(uuid.uuid4())
        product_data["created_at"] = datetime.now().isoformat()
        product_data["updated_at"] = datetime.now().isoformat()
        await db.add_document(self.collection_path, product_data)
        return Product(**product_data)

    async def get_product(self, product_id: str) -> Product:
        product_data = await db.get_document(self.collection_path, product_id)
        if not product_data:
            raise ProductNotFound(f"Product with ID {product_id} not found")
        return Product(**product_data)

    async def get_all_products(self, limit: int = 10, offset: int = 0, 
                               category_id: Optional[str] = None, in_stock: Optional[bool] = None) -> List[Product]:
        filters = {}
        if category_id:
            filters["category_id"] = category_id
        
        products_data = await db.query_collection(self.collection_path, filters=filters, limit=limit, offset=offset)
        
        products = [Product(**data) for data in products_data]

        if in_stock is not None:
            products = [p for p in products if (p.stock_quantity > 0) == in_stock]

        return products

    async def update_product(self, product_id: str, product_data: Dict[str, Any]) -> Product:
        updated_data = await db.update_document(self.collection_path, product_id, product_data)
        if not updated_data:
            raise ProductNotFound(f"Product with ID {product_id} not found")
        return Product(**updated_data)

    async def delete_product(self, product_id: str):
        if not await db.delete_document(self.collection_path, product_id):
            raise ProductNotFound(f"Product with ID {product_id} not found")

    async def search_products(self, query: str, limit: int = 10, offset: int = 0) -> List[Product]:
        all_products = await db.query_collection(self.collection_path)
        results = []
        for product_data in all_products:
            product = Product(**product_data)
            if query.lower() in product.name.lower() or \
               (product.description and query.lower() in product.description.lower()):
                results.append(product)
        
        # Apply pagination after search
        return results[offset:offset+limit]

    async def update_product_stock(self, product_id: str, quantity_change: int) -> Product:
        product = await self.get_product(product_id)
        new_stock = product.stock_quantity + quantity_change
        if new_stock < 0:
            raise InsufficientStock(f"Not enough stock for product {product_id}")
        return await self.update_product(product_id, {"stock_quantity": new_stock})

class CategoryService:
    def __init__(self):
        self.collection_path = f"/artifacts/{APP_ID}/public/data/categories"

    async def create_category(self, category: Category) -> Category:
        category_data = category.dict()
        category_data["category_id"] = str(uuid.uuid4())
        category_data["created_at"] = datetime.now().isoformat()
        category_data["updated_at"] = datetime.now().isoformat()
        await db.add_document(self.collection_path, category_data)
        return Category(**category_data)

    async def get_category(self, category_id: str) -> Category:
        category_data = await db.get_document(self.collection_path, category_id)
        if not category_data:
            raise CategoryNotFound(f"Category with ID {category_id} not found")
        return Category(**category_data)

    async def get_all_categories(self, limit: int = 10, offset: int = 0) -> List[Category]:
        categories_data = await db.query_collection(self.collection_path, limit=limit, offset=offset)
        return [Category(**data) for data in categories_data]

    async def update_category(self, category_id: str, category_data: Dict[str, Any]) -> Category:
        updated_data = await db.update_document(self.collection_path, category_id, category_data)
        if not updated_data:
            raise CategoryNotFound(f"Category with ID {category_id} not found")
        return Category(**updated_data)

    async def delete_category(self, category_id: str):
        if not await db.delete_document(self.collection_path, category_id):
            raise CategoryNotFound(f"Category with ID {category_id} not found")

class CartService:
    def __init__(self):
        self.base_path = f"/artifacts/{APP_ID}/users"
        self.product_service = ProductService()

    async def _get_cart_path(self, user_id: str) -> str:
        return f"{self.base_path}/{user_id}/carts"

    async def get_cart(self, user_id: str) -> Cart:
        cart_data = await db.get_document(await self._get_cart_path(user_id), user_id) # Assuming user_id is also doc_id for cart
        if not cart_data:
            # Create an empty cart if it doesn't exist
            new_cart = Cart(user_id=user_id, items=[])
            await db.add_document(await self._get_cart_path(user_id), new_cart.dict())
            return new_cart
        return Cart(**cart_data)

    async def add_item_to_cart(self, user_id: str, product_id: str, quantity: int) -> Cart:
        cart = await self.get_cart(user_id)
        product = await self.product_service.get_product(product_id)

        existing_item_index = -1
        for i, item in enumerate(cart.items):
            if item.product_id == product_id:
                existing_item_index = i
                break

        if existing_item_index != -1:
            cart.items[existing_item_index].quantity += quantity
        else:
            cart.items.append(CartItem(product_id=product_id, quantity=quantity, price_at_addition=product.price))
        
        cart.updated_at = datetime.now()
        await db.update_document(await self._get_cart_path(user_id), user_id, cart.dict())
        return cart

    async def update_cart_item_quantity(self, user_id: str, product_id: str, quantity: int) -> Cart:
        cart = await self.get_cart(user_id)
        found = False
        for item in cart.items:
            if item.product_id == product_id:
                item.quantity = quantity
                found = True
                break
        if not found:
            raise ProductNotFound(f"Product {product_id} not in cart")
        
        cart.updated_at = datetime.now()
        await db.update_document(await self._get_cart_path(user_id), user_id, cart.dict())
        return cart

    async def remove_item_from_cart(self, user_id: str, product_id: str) -> Cart:
        cart = await self.get_cart(user_id)
        original_len = len(cart.items)
        cart.items = [item for item in cart.items if item.product_id != product_id]
        if len(cart.items) == original_len:
            raise ProductNotFound(f"Product {product_id} not in cart")
        
        cart.updated_at = datetime.now()
        await db.update_document(await self._get_cart_path(user_id), user_id, cart.dict())
        return cart

class OrderService:
    def __init__(self):
        self.base_path = f"/artifacts/{APP_ID}/users"
        self.product_service = ProductService()
        self.cart_service = CartService()

    async def _get_orders_path(self, user_id: str) -> str:
        return f"{self.base_path}/{user_id}/orders"

    async def create_order_from_cart(self, user_id: str) -> Order:
        cart = await self.cart_service.get_cart(user_id)
        if not cart.items:
            raise CartNotFound("Cart is empty, cannot create order")

        order_items = []
        total_amount = 0.0
        
        # Simulate atomic inventory management
        for item in cart.items:
            product = await self.product_service.get_product(item.product_id)
            if product.stock_quantity < item.quantity:
                raise InsufficientStock(f"Not enough stock for product {product.name}")
            
            # "Lock" stock by reducing it immediately
            await self.product_service.update_product_stock(product.product_id, -item.quantity)
            
            order_items.append(OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=item.price_at_addition
            ))
            total_amount += item.quantity * item.price_at_addition

        order_id = str(uuid.uuid4())
        order_data = {
            "order_id": order_id,
            "user_id": user_id,
            "total_amount": total_amount,
            "status": "pending",
            "order_items": [item.dict() for item in order_items],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        await db.add_document(await self._get_orders_path(user_id), order_data)
        
        # Clear the cart after order creation
        cart.items = []
        await db.update_document(await self._get_cart_path(user_id), user_id, cart.dict())

        return Order(**order_data)

    async def get_order(self, user_id: str, order_id: str) -> Order:
        order_data = await db.get_document(await self._get_orders_path(user_id), order_id)
        if not order_data:
            raise OrderNotFound(f"Order with ID {order_id} not found for user {user_id}")
        return Order(**order_data)

    async def get_all_orders(self, user_id: str, limit: int = 10, offset: int = 0) -> List[Order]:
        orders_data = await db.query_collection(await self._get_orders_path(user_id), limit=limit, offset=offset)
        return [Order(**data) for data in orders_data]

    async def update_order_status(self, user_id: str, order_id: str, new_status: str) -> Order:
        order = await self.get_order(user_id, order_id)
        updated_data = await db.update_document(await self._get_orders_path(user_id), order_id, {"status": new_status})
        if not updated_data:
            raise OrderNotFound(f"Order with ID {order_id} not found")
        return Order(**updated_data)

class ReviewService:
    def __init__(self):
        self.collection_path = f"/artifacts/{APP_ID}/public/data/product_reviews"
        self.product_service = ProductService()

    async def create_review(self, product_id: str, user_id: str, rating: int, comment: Optional[str] = None) -> Review:
        # Ensure product exists
        await self.product_service.get_product(product_id)

        review_id = str(uuid.uuid4())
        review_data = {
            "review_id": review_id,
            "product_id": product_id,
            "user_id": user_id,
            "rating": rating,
            "comment": comment,
            "is_approved": False, # Reviews need to be approved by default
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        await db.add_document(self.collection_path, review_data)
        return Review(**review_data)

    async def get_reviews_for_product(self, product_id: str, limit: int = 10, offset: int = 0) -> List[Review]:
        reviews_data = await db.query_collection(self.collection_path, filters={"product_id": product_id}, limit=limit, offset=offset)
        return [Review(**data) for data in reviews_data]

    async def calculate_average_rating(self, product_id: str) -> float:
        reviews = await self.get_reviews_for_product(product_id, limit=1000) # Fetch all for calculation
        if not reviews:
            return 0.0
        total_rating = sum(review.rating for review in reviews)
        return total_rating / len(reviews)

class PromoCodeService:
    def __init__(self):
        self.collection_path = f"/artifacts/{APP_ID}/public/data/promo_codes"

    async def create_promo_code(self, promo_code: PromoCode) -> PromoCode:
        promo_data = promo_code.dict()
        promo_data["promo_code_id"] = str(uuid.uuid4())
        promo_data["created_at"] = datetime.now().isoformat()
        promo_data["updated_at"] = datetime.now().isoformat()
        await db.add_document(self.collection_path, promo_data)
        return PromoCode(**promo_data)

    async def get_promo_code_by_code(self, code: str) -> PromoCode:
        promo_codes = await db.query_collection(self.collection_path, filters={"code": code})
        if not promo_codes:
            raise PromoCodeNotFound(f"Promo code '{code}' not found")
        return PromoCode(**promo_codes[0])

    async def get_all_promo_codes(self, limit: int = 10, offset: int = 0) -> List[PromoCode]:
        promo_codes_data = await db.query_collection(self.collection_path, limit=limit, offset=offset)
        return [PromoCode(**data) for data in promo_codes_data]

    async def apply_promo_code_to_cart(self, cart: Cart, promo_code_str: str) -> float:
        promo_code = await self.get_promo_code_by_code(promo_code_str)

        if not promo_code.is_active:
            raise InvalidPromoCode("Promo code is not active")
        if promo_code.expiry_date < datetime.now():
            raise InvalidPromoCode("Promo code has expired")
        if promo_code.usage_limit is not None and promo_code.times_used >= promo_code.usage_limit:
            raise InvalidPromoCode("Promo code usage limit reached")

        # Check applicability to products/categories in cart
        applicable_items_total = 0.0
        for item in cart.items:
            product = await self.product_service.get_product(item.product_id)
            is_applicable = False
            if not promo_code.applicable_products and not promo_code.applicable_categories:
                is_applicable = True # Applies to all if no specific restrictions
            elif promo_code.applicable_products and product.product_id in promo_code.applicable_products:
                is_applicable = True
            elif promo_code.applicable_categories and product.category_id in promo_code.applicable_categories:
                is_applicable = True
            
            if is_applicable:
                applicable_items_total += item.quantity * item.price_at_addition
        
        if applicable_items_total == 0:
            raise InvalidPromoCode("Promo code not applicable to any items in cart")

        discount_amount = applicable_items_total * (promo_code.discount_percentage / 100.0)
        
        # Increment usage count (in a real system, this would be part of order finalization)
        promo_code.times_used += 1
        await db.update_document(self.collection_path, promo_code.promo_code_id, {"times_used": promo_code.times_used})

        return discount_amount

user_service = UserService()
product_service = ProductService()
category_service = CategoryService()
cart_service = CartService()
order_service = OrderService()
review_service = ReviewService()
promo_code_service = PromoCodeService()