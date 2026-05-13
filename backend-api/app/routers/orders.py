from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database

router = APIRouter(prefix="/orders", tags=["Orders Management"])        

@router.post("/", response_model=schemas.OrderOut)
def create_order(order: schemas.OrderCreate, db: Session = Depends(database.get_db)):
    # 1. Lưu thông tin chung của đơn hàng
    db_order = models.Order(
        user_id=order.user_id,
        total=order.total,
        status="pending", # Đơn mới luôn ở trạng thái chờ
        shipping_address=order.shipping_address,
        payment_method=order.payment_method
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order) # Lấy ID đơn hàng vừa tạo

    # 2. Lưu từng sản phẩm vào Order_Items
    for item in order.items:
        db_order_item = models.OrderDetail(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price
        )
        db.add(db_order_item)
    
    # 3. Xóa giỏ hàng của user sau khi đặt hàng thành công
    db.query(models.Cart).filter(models.Cart.user_id == order.user_id).delete()
    
    db.commit()
    return db_order

# API cho Web Admin lấy danh sách tất cả đơn hàng
@router.get("/", response_model=List[schemas.OrderOut])
def get_all_orders(db: Session = Depends(database.get_db)):
    # Sắp xếp đơn hàng mới nhất lên đầu
    orders = db.query(models.Order).order_by(models.Order.created_at.desc()).all()
    return orders

@router.patch("/{order_id}/status", response_model=schemas.OrderOut)
def update_order_status(
    order_id: int, 
    order_update: schemas.OrderStatusUpdate, 
    db: Session = Depends(database.get_db)
):
    # Tìm đơn hàng trong database
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    
    if not db_order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")

    # Cập nhật trạng thái mới
    db_order.status = order_update.status
    db.commit()
    db.refresh(db_order)
    
    return db_order