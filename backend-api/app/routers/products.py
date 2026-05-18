from fastapi import APIRouter, Depends, HTTPException, status
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
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
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

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(database.get_db)):
    # 1. Tìm sản phẩm trong Database
    product_query = db.query(models.Product).filter(models.Product.id == product_id)
    product = product_query.first()
    
    # 2. Nếu không có sản phẩm nào có ID này -> Báo lỗi
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm cần xóa")
    
    # 3. Tiến hành xóa và lưu thay đổi vào DB
    product_query.delete(synchronize_session=False)
    db.commit()
    
    return {"message": f"Đã xóa thành công sản phẩm có ID: {product_id}"}

@router.put("/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    # 1. Tìm sản phẩm trong DB
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy sản phẩm")

    # 2. Cập nhật các trường có gửi lên
    update_data = product.dict(exclude_unset=True) # Chỉ lấy các trường có giá trị truyền vào
    for key, value in update_data.items():
        setattr(db_product, key, value)

    # 3. Lưu vào database
    db.commit()
    db.refresh(db_product)
    return db_product