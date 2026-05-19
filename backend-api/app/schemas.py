from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# SCHEMAS CHO CATEGORY
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True  

# SCHEMAS CHO PRODUCT
class ProductBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    
    # ⚠️ QUAN TRỌNG: Sửa thành 'image' (không dùng image_url nữa)
    image: Optional[str] = None 
    
    # Khai báo thêm các trường có trong Database để Web Admin và App có thể đọc được
    category: Optional[str] = None
    category_id: Optional[int] = None

    created_at: Optional[datetime] = datetime.now()

    brand: Optional[str] = None
    color: Optional[str] = None
    stock_quantity: Optional[int] = 0
    material: Optional[str] = None
    gender: Optional[str] = "Unisex"
    season: Optional[str] = None
    style: Optional[str] = None
    is_active: Optional[bool] = True

# Schema dùng để trả dữ liệu về cho Client (App/Web)
class Product(ProductBase):
    id: int
    category_rel: Optional[Category] = None  
    
    class Config:
        from_attributes = True


# Khuôn dùng để nhận dữ liệu khi Tạo mới
class ProductCreate(ProductBase):
    pass

# Khuôn dùng để Trả dữ liệu về cho Web/App
class ProductResponse(ProductBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True # (hoặc orm_mode = True nếu bạn đang dùng Pydantic bản cũ)

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None
    image: Optional[str] = None


# SCHEMAS CHO GIỎ HÀNG
class CartItemBase(BaseModel):
    product_id: int
    quantity: int = 1
    color: Optional[str] = None
    size: Optional[str] = None

class CartItemCreate(CartItemBase):
    user_id: int 

class CartItemOut(CartItemBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

# SCHEMAS CHO ĐƠN HÀNG (CHECKOUT)
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderItemOut(OrderItemBase):
    id: int
    # Sử dụng class Product (đã khai báo ở trên) để lồng thông tin tên, hình ảnh,...
    product: Optional[Product] = None 

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    user_id: int
    total: float
    shipping_address: str
    payment_method: str
    items: List[OrderItemBase]

class OrderStatusUpdate(BaseModel):
    status: str  # Ví dụ: 'processing', 'shipped', 'completed', 'cancelled'

class OrderOut(BaseModel):
    id: int
    user_id: int
    total: float
    status: str
    shipping_address: str
    payment_method: str
    created_at: datetime
    
    items: List[OrderItemOut] = []

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None # Cho phép không nhập mật khẩu khi cập nhật

class UserOut(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

# --- SCHEMAS CHO ADMIN ---
class AdminBase(BaseModel):
    username: str
    full_name: str
    role: str

class AdminCreate(AdminBase):
    password: str

class AdminUpdate(AdminBase):
    password: Optional[str] = None # Cho phép không nhập mật khẩu khi sửa

class AdminOut(AdminBase):
    id: int

    class Config:
        from_attributes = True

class AdminLogin(BaseModel):
    username: str
    password: str
