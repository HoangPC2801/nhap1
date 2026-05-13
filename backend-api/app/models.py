from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, Boolean, TIMESTAMP, text, DECIMAL, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(255))
    email = Column(String(100), unique=True, index=True)
    full_name = Column(String(100))
    address = Column(Text)
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    
    # Quan hệ với bảng Orders
    orders = relationship("Order", back_populates="owner")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text)
    
    # Quan hệ 1-N với Products
    products = relationship("Product", back_populates="category_rel")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    image = Column(String(1000), nullable=True) 
    
    category = Column(String(50), nullable=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category_rel = relationship("Category", back_populates="products")
    brand = Column(String(50), nullable=True, index=True)
    
    # Tự động lấy giờ hệ thống khi tạo và cập nhật
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Các thuộc tính chi tiết của giày
    color = Column(String(50), nullable=True)
    stock_quantity = Column(Integer, default=0)
    material = Column(String(100), nullable=True)
    
    # Kiểu Enum cho giới tính
    gender = Column(Enum('Nam', 'Nữ', 'Unisex'), default='Unisex')
    season = Column(String(50), nullable=True)
    style = Column(String(100), nullable=True)
    
    # Trong SQLAlchemy, Boolean sẽ tự động map với tinyint(1) trong MySQL
    is_active = Column(Boolean, default=True)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total = Column(Float)
    status = Column(String(20), default="pending")
    shipping_address = Column(Text)
    payment_method = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    owner = relationship("User", back_populates="orders")
    items = relationship("OrderDetail", back_populates="order")

class OrderDetail(Base):
    __tablename__ = "order_items" 

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    price = Column(Float)

    order = relationship("Order", back_populates="items")

class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    color = Column(String(50))
    size = Column(String(10))
    
    product = relationship("Product")

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False) # Chú ý: Cột này lưu mật khẩu đã mã hóa
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default="manager") # Phân quyền: 'manager' hoặc 'superadmin'