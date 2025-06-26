# E-commerce Backend API

This is a complete, maintainable, and scalable backend API for a full-featured e-commerce platform built with FastAPI, using a mocked Firestore (in-memory dictionary for now, to be replaced with SQLite) for data persistence.

## Features

- **Authentication**: JWT + Mocked Firebase Auth
- **Products**: Full CRUD operations with search, pagination, filtering, and sorting.
- **Categories**: CRUD operations with support for nested categories.
- **Shopping Cart**: Add, update, remove items, and retrieve cart contents.
- **Orders**: Create orders from cart, retrieve orders, simulate payment.
- **Product Reviews**: Add reviews, retrieve reviews for a product, calculate average rating.
- **Promo Codes**: Admin-only creation, retrieval, and application to cart with validation.
- **Atomic Inventory Management**: Simulated stock locking during order creation.
- **Error Handling**: Custom exceptions for various scenarios.
- **Pydantic Models**: For data validation and serialization.
- **Code Organization**: Modular structure with dedicated files for models, services, exceptions, and routes.

## Project Structure

```
ecommerce_api/
│
├── main.py               # FastAPI entry point
├── auth.py               # Firebase & JWT auth utils
├── models.py             # Pydantic models
├── services.py           # Business logic
├── firestore.py          # Mocked Firestore client utils (in-memory dict)
├── exceptions.py         # Custom errors
├── routes/
│   ├── users.py
│   ├── products.py
│   ├── categories.py
│   ├── cart.py
│   ├── orders.py
│   ├── reviews.py
│   └── promos.py
└── README.md             # Usage instructions
```

## Setup and Running

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/E-commerce-Backend-API.git
    cd E-commerce-Backend-API
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment**:
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the application**:
    ```bash
    uvicorn ecommerce_api.main:app --reload
    ```

    The API will be accessible at `http://127.0.0.1:8000`.

## API Endpoints

Refer to the automatically generated OpenAPI documentation at `http://127.0.0.1:8000/docs` for a complete list of endpoints and their specifications.

## Mocked Data and Assumptions

-   **Firestore**: Currently mocked using an in-memory dictionary. Data will not persist across restarts.
-   **Firebase Auth**: Simulated. `current_user_id = "demo_user"` is used as a placeholder.
-   **Admin User**: For routes requiring admin privileges, a user with `user_id = "admin_user"` is assumed to be an admin.
-   **Payment**: Simulated success via a dedicated endpoint.

## Future Enhancements

-   Replace mocked Firestore with a persistent SQLite database.
-   Implement proper user management and roles.
-   Add more sophisticated search capabilities.
-   Integrate with a real payment gateway (e.g., Stripe, PayPal).
-   Implement comprehensive testing.# E-commerce-API
