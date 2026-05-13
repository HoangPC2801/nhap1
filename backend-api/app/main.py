from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routers import products, categories, cart, orders, users, admins, dashboard

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hệ thống Bán Giày API",
    description="API Backend cho đồ án tốt nghiệp hệ thống bán giày",
    version="1.0.0"
)

# CẤU HÌNH CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500", 
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả các phương thức GET, POST, PUT, DELETE
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(categories.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(users.router)
app.include_router(admins.router)
app.include_router(dashboard.router)

@app.get("/")
def home():
    return {"message": "API BizFlow đang chạy. Truy cập /docs để xem tài liệu."}