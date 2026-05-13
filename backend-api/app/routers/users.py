from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import List
from .. import models, schemas, database

# Khởi tạo công cụ mã hóa mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/users", tags=["Users Management"])

# Hàm tiện ích mã hóa mật khẩu
def get_password_hash(password: str):
    return pwd_context.hash(password)

# 1. API: Lấy danh sách người dùng
@router.get("/", response_model=List[schemas.UserOut])
def get_all_users(db: Session = Depends(database.get_db)):
    users = db.query(models.User).order_by(models.User.id.desc()).all()
    return users

# 2. API: Thêm người dùng mới
@router.post("/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Kiểm tra xem username hoặc email đã tồn tại chưa
    existing_user = db.query(models.User).filter(
        (models.User.username == user.username) | (models.User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Tên đăng nhập hoặc Email đã tồn tại!")

    # Mã hóa mật khẩu trước khi lưu
    hashed_password = get_password_hash(user.password)
    
    new_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        address=user.address,
        password=hashed_password,
        is_active=True # Mặc định kích hoạt khi tạo mới
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 3. API: Cập nhật thông tin người dùng
@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    # Kiểm tra xem email mới cập nhật có trùng với người khác không
    if user_update.email != db_user.email:
        email_check = db.query(models.User).filter(models.User.email == user_update.email).first()
        if email_check:
            raise HTTPException(status_code=400, detail="Email này đã được sử dụng!")

    # Cập nhật các trường thông tin cơ bản
    db_user.email = user_update.email
    db_user.full_name = user_update.full_name
    db_user.phone = user_update.phone
    db_user.address = user_update.address

    # Nếu Admin có nhập mật khẩu mới thì tiến hành mã hóa và cập nhật
    if user_update.password:
        db_user.password = get_password_hash(user_update.password)

    db.commit()
    db.refresh(db_user)
    return db_user

# 4. API: Kích hoạt / Vô hiệu hóa người dùng
@router.patch("/{user_id}/toggle-active", response_model=schemas.UserOut)
def toggle_user_active(user_id: int, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    # Đảo ngược trạng thái: True thành False, False thành True
    db_user.is_active = not db_user.is_active
    db.commit()
    db.refresh(db_user)
    return db_user

# 5. API: Xóa người dùng
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    try:
        db.delete(db_user)
        db.commit()
        return {"message": "Đã xóa người dùng thành công"}
    except Exception as e:
        # Bắt lỗi trường hợp user đã có đơn hàng (lỗi khóa ngoại foreign key)
        raise HTTPException(status_code=400, detail="Không thể xóa do người dùng này đã có dữ liệu liên quan (Đơn hàng, v.v...)")