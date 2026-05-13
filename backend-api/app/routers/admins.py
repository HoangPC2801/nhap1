from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import List
from .. import models, schemas, database

# Tái sử dụng công cụ mã hóa mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/admins", tags=["Admins Management"])

def get_password_hash(password: str):
    return pwd_context.hash(password)

# 1. API: Lấy danh sách Quản trị viên
@router.get("/", response_model=List[schemas.AdminOut])
def get_all_admins(db: Session = Depends(database.get_db)):
    admins = db.query(models.Admin).order_by(models.Admin.id.desc()).all()
    return admins

# 2. API: Thêm Quản trị viên mới
@router.post("/", response_model=schemas.AdminOut)
def create_admin(admin: schemas.AdminCreate, db: Session = Depends(database.get_db)):
    # Kiểm tra xem tên đăng nhập đã tồn tại chưa
    existing_admin = db.query(models.Admin).filter(models.Admin.username == admin.username).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Tên đăng nhập này đã tồn tại!")

    # Mã hóa mật khẩu
    hashed_password = get_password_hash(admin.password)
    
    new_admin = models.Admin(
        username=admin.username,
        full_name=admin.full_name,
        role=admin.role,
        password_hash=hashed_password # Lưu ý tên cột trong DB của bạn (có thể là password hoặc password_hash)
    )
    
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

# 3. API: Cập nhật thông tin Quản trị viên
@router.put("/{admin_id}", response_model=schemas.AdminOut)
def update_admin(admin_id: int, admin_update: schemas.AdminUpdate, db: Session = Depends(database.get_db)):
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not db_admin:
        raise HTTPException(status_code=404, detail="Không tìm thấy quản trị viên")

    # Kiểm tra nếu đổi username thì có bị trùng với người khác không
    if admin_update.username != db_admin.username:
        username_check = db.query(models.Admin).filter(models.Admin.username == admin_update.username).first()
        if username_check:
            raise HTTPException(status_code=400, detail="Tên đăng nhập này đã được sử dụng!")

    # Cập nhật thông tin
    db_admin.username = admin_update.username
    db_admin.full_name = admin_update.full_name
    db_admin.role = admin_update.role

    # Chỉ cập nhật mật khẩu nếu có nhập mật khẩu mới
    if admin_update.password:
        db_admin.password_hash = get_password_hash(admin_update.password)

    db.commit()
    db.refresh(db_admin)
    return db_admin

# 4. API: Xóa Quản trị viên
@router.delete("/{admin_id}")
def delete_admin(admin_id: int, db: Session = Depends(database.get_db)):
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not db_admin:
        raise HTTPException(status_code=404, detail="Không tìm thấy quản trị viên")

    try:
        db.delete(db_admin)
        db.commit()
        return {"message": "Đã xóa quản trị viên thành công"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi khi xóa: {str(e)}")
    
# Hàm so sánh mật khẩu nhập vào với mật khẩu đã mã hóa trong DB
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/login")
def login_admin(login_data: schemas.AdminLogin, db: Session = Depends(database.get_db)):
    # 1. Tìm quản trị viên trong Database dựa vào username
    admin_user = db.query(models.Admin).filter(
        models.Admin.username == login_data.username
    ).first()

    # 2. Nếu không tìm thấy username
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Tên đăng nhập không tồn tại!"
        )

    # 3. Nếu tìm thấy, tiếp tục kiểm tra mật khẩu
    is_password_valid = verify_password(login_data.password, admin_user.password_hash)
    if not is_password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Mật khẩu không chính xác!"
        )

    # 4. Nếu mọi thứ đúng chuẩn, trả về thông tin cho Frontend lưu vào LocalStorage
    return {
        "id": admin_user.id,
        "username": admin_user.username,
        "role": admin_user.role
    }