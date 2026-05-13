from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, database

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(database.get_db)):
    # 1. Đếm tổng số đơn hàng[cite: 6]
    total_orders = db.query(models.Order).count()
    
    # 2. Tính tổng doanh thu của các đơn 'completed'[cite: 6]
    total_revenue = db.query(func.sum(models.Order.total)).filter(models.Order.status == 'completed').scalar()
    
    # 3. Đếm số sản phẩm (nếu model Product có is_active thì thêm .filter(models.Product.is_active == True))[cite: 6]
    total_products = db.query(models.Product).count()
    
    # 4. Đếm số người dùng đang hoạt động[cite: 6]
    total_users = db.query(models.User).filter(models.User.is_active == True).count()

    return {
        "total_orders": total_orders,
        "total_revenue": total_revenue or 0, # Tránh trường hợp null nếu chưa có đơn nào
        "total_products": total_products,
        "total_users": total_users
    }