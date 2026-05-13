from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database
from ..database import get_db

router = APIRouter(
    prefix="/products",
    tags=["Products"] 
)

@router.get("/", response_model=List[schemas.Product])
def get_all_products(db: Session = Depends(database.get_db)):
    products = db.query(models.Product).all()
    return products

@router.get("/{product_id}", response_model=schemas.Product)
def get_product(product_id: int, db: Session = Depends(database.get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy đôi giày này")
    return product

@router.post("/", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    # 1. Chuyển đổi dữ liệu Pydantic (đã có sẵn link ảnh) thành Model SQLAlchemy
    new_product = models.Product(**product.model_dump()) # (dùng .dict() nếu Pydantic cũ)
    
    # 2. Lưu trực tiếp vào MySQL
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product