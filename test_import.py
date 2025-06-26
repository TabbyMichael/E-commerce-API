import sys
sys.path.append('c:\\Users\\Administrator\\Documents\\GitHub\\E-commerce Backend API')

try:
    from ecommerce_api.user_service import UserService
    print("UserService imported successfully!")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")