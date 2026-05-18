from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, database

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(database.get_db)):
    # 1. Tổng đơn hàng
    total_orders = db.query(models.Order).count()
    
    # 2. Tổng doanh thu (chỉ tính đơn 'completed')
    total_revenue = db.query(func.sum(models.Order.total)).filter(models.Order.status == 'completed').scalar() or 0
    
    # 3. Tổng sản phẩm đang bán
    # (Nếu bảng product không có cột is_active, bạn bỏ đoạn .filter() đi)
    total_products = db.query(models.Product).filter(models.Product.is_active == True).count()
    
    # 4. Tổng người dùng
    total_users = db.query(models.User).filter(models.User.is_active == True).count()

    # 5. Lấy 10 đơn hàng gần nhất (kèm tên User)
    recent_orders_query = db.query(models.Order, models.User.username)\
        .join(models.User, models.Order.user_id == models.User.id)\
        .order_by(models.Order.created_at.desc()).limit(10).all()

    recent_orders = []
    for order, username in recent_orders_query:
        recent_orders.append({
            "id": order.id,
            "created_at": order.created_at,
            "username": username,
            "total": order.total,
            "status": order.status
        })

    return {
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "total_products": total_products,
        "total_users": total_users,
        "recent_orders": recent_orders
    }