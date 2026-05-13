from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.post("/", response_model=schemas.CartItemOut)
def add_to_cart(item: schemas.CartItemCreate, db: Session = Depends(database.get_db)):
    # 1. Kiểm tra sản phẩm có tồn tại không
    product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")

    # 2. Tạo bản ghi giỏ hàng mới
    db_cart_item = models.Cart(
        user_id=item.user_id,
        product_id=item.product_id,
        quantity=item.quantity,
        color=item.color,
        size=item.size
    )
    db.add(db_cart_item)
    db.commit()
    db.refresh(db_cart_item)
    return db_cart_item

@router.get("/{user_id}", response_model=List[schemas.CartItemOut])
def get_user_cart(user_id: int, db: Session = Depends(database.get_db)):
    return db.query(models.Cart).filter(models.Cart.user_id == user_id).all()