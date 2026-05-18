from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from .. import models, database

router = APIRouter(prefix="/orders", tags=["Orders"])

# 1. Lấy danh sách kèm theo lọc trạng thái
@router.get("/")
def get_orders(status: Optional[str] = None, db: Session = Depends(database.get_db)):
    query = db.query(models.Order, models.User.username).join(models.User, models.Order.user_id == models.User.id)
    if status:
        query = query.filter(models.Order.status == status)
        
    orders_data = query.order_by(models.Order.created_at.desc()).all()
    
    result = []
    for order, username in orders_data:
        result.append({
            "id": order.id,
            "created_at": order.created_at,
            "total": order.total,
            "status": order.status,
            "username": username
        })
    return result

# 2. Cập nhật trạng thái / Hủy đơn hàng
@router.put("/{order_id}/status")
def update_order_status(order_id: int, status: str, db: Session = Depends(database.get_db)):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
    
    # Logic: Chỉ cho phép hủy khi đơn hàng đang pending
    if status == 'cancelled' and db_order.status != 'pending':
        raise HTTPException(status_code=400, detail="Chỉ có thể hủy đơn hàng ở trạng thái pending")
        
    db_order.status = status
    db.commit()
    return {"message": "Cập nhật thành công"}

@router.get("/{order_id}")
def get_order_detail(order_id: int, db: Session = Depends(database.get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
    
    items_query = db.query(models.OrderDetail, models.Product.name, models.Product.image_url)\
        .join(models.Product, models.OrderDetail.product_id == models.Product.id)\
        .filter(models.OrderDetail.order_id == order_id).all()
    
    order_items = []
    for item, prod_name, prod_image in items_query:
        order_items.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": prod_name,
            "image_url": prod_image,
            "quantity": item.quantity,
            "price": item.price,
            "total_price": item.quantity * item.price
        })
    
    return {
        "id": order.id,
        "created_at": order.created_at,
        "total": order.total,
        "status": order.status,
        "user_id": order.user_id,
        "order_items": order_items 
    }