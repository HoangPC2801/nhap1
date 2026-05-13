const adminRole = localStorage.getItem('admin_role') || 'manager';

let superAdminMenu = '';
if (adminRole === 'superadmin') {
    superAdminMenu = `<li class="nav-item">
        <a class="nav-link text-white" href="admin-admins.html">Quản trị viên</a>
    </li>`;
}

// Header (Navbar)
const adminHeaderHTML = `
<div class="header-wrapper bg-dark text-white p-3 mb-4">
    <div class="header-container container d-flex justify-content-between align-items-center">
        
        <div class="logo">
            <a href="admin-dashboard.html" class="text-white text-decoration-none fs-4 fw-bold">
                ShoeStore Admin
            </a>
        </div>

        <nav class="main-nav">
            <ul class="nav">
                <li class="nav-item">
                    <a class="nav-link text-white" href="admin-dashboard.html">Bảng điều khiển</a>
                </li>

                <li class="nav-item">
                    <a class="nav-link text-white" href="admin-products.html">Sản phẩm</a>
                </li>

                <li class="nav-item">
                    <a class="nav-link text-white" href="admin-orders.html">Đơn hàng</a>
                </li>

                <li class="nav-item">
                    <a class="nav-link text-white" href="admin-users.html">Người dùng</a>
                </li>

                ${superAdminMenu}

                <li class="nav-item">
                    <a class="nav-link text-danger" href="#" onclick="handleLogout()">Đăng xuất</a>
                </li>
            </ul>
        </nav>
    </div>
</div>
`;

// Footer
const adminFooterHTML = `
<footer class="bg-dark text-white pt-5 pb-3 mt-auto">
    <div class="container">
        <div class="row">
            <div class="col-md-4 mb-3">
                <h5 class="text-uppercase text-primary">Về chúng tôi</h5>
                <p class="small text-light">
                    BizFlow Admin - Hệ thống quản lý cửa hàng giày uy tín, chất lượng hàng đầu Việt Nam.
                </p>
            </div>
            <div class="col-md-4 mb-3">
                <h5 class="text-uppercase text-primary">Liên hệ</h5>
                <p class="small text-light mb-1">- Email: admin@bizflow.com</p>
                <p class="small text-light">- Điện thoại: 0123 456 789</p>
            </div>
            <div class="col-md-4 mb-3">
                <h5 class="text-uppercase text-primary">Địa chỉ</h5>
                <p class="small text-light">
                    - 123 Đường ABC, TP. Hồ Chí Minh
                </p>
            </div>
        </div>

        <hr class="border-secondary my-3">

        <div class="text-center small text-light">
            <p class="mb-0">&copy; 2026 BizFlow Admin. All rights reserved.</p>
        </div>
    </div>
</footer>
`;

// Load Header + Footer
function loadLayout() {
    const headerEl = document.getElementById('admin-header');
    const footerEl = document.getElementById('admin-footer');

    if (headerEl) headerEl.innerHTML = adminHeaderHTML;
    if (footerEl) footerEl.innerHTML = adminFooterHTML;

    // Highlight menu active
    const currentPath = window.location.pathname.split('/').pop();

    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// Logout
function handleLogout() {
    if (confirm("Bạn có chắc chắn muốn đăng xuất?")) {
        localStorage.removeItem('admin_role');
        localStorage.removeItem('admin_id');
        localStorage.removeItem('admin_token');

        window.location.href = 'admin-login.html';
    }
}

// 7. Auto load
document.addEventListener('DOMContentLoaded', loadLayout);

// 1. Khởi tạo Firebase (Dán đoạn mã bạn copy ở Giai đoạn 1 vào đây)
const firebaseConfig = {
  apiKey: "AIzaSyCyuP7fgmTj0yPQh_3J8-IC7kl8QoLpqvE",
  authDomain: "appbangiay-dac0f.firebaseapp.com",
  projectId: "appbangiay-dac0f",
  storageBucket: "appbangiay-dac0f.firebasestorage.app",
  messagingSenderId: "641802044909",
  appId: "1:641802044909:web:25d85ecbae1be8f00393e4",
  measurementId: "G-R9HPQE536Z"
};

// Kiểm tra tránh khởi tạo lại nếu đã khởi tạo
if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
}
const storage = firebase.storage();

// 2. Hàm xử lý khi bấm nút "Lưu sản phẩm"
async function handleAddProduct() {
    const fileInput = document.getElementById('productImage'); // ID của ô chọn file <input type="file">
    const file = fileInput.files[0];
    
    if (!file) {
        alert("Vui lòng chọn một tấm ảnh cho sản phẩm!");
        return;
    }

    // Hiển thị trạng thái đang tải
    document.getElementById('submitBtn').innerText = "Đang tải ảnh lên...";

    try {
        // Tạo tên file ngẫu nhiên để không bị trùng (vd: giay-nike-123456.jpg)
        const uniqueFileName = new Date().getTime() + '-' + file.name;
        
        // Trỏ tới thư mục 'products/' trên Firebase Storage
        const storageRef = storage.ref('products/' + uniqueFileName);
        
        // Tiến hành đẩy file lên
        const snapshot = await storageRef.put(file);
        
        // Lấy đường link URL công khai của ảnh vừa đẩy
        const downloadURL = await snapshot.ref.getDownloadURL();
        console.log("Link ảnh đã lấy được:", downloadURL);

        // 3. Gửi thông tin (kèm link ảnh) về FastAPI Backend
        await saveToFastAPI(downloadURL);

    } catch (error) {
        console.error("Lỗi khi tải ảnh lên Firebase:", error);
        alert("Có lỗi xảy ra khi tải ảnh!");
    }
}

// Hàm gửi dữ liệu về Server Python
async function saveToFastAPI(imageUrl) {
    
    // 1. Lấy và ép kiểu dữ liệu cẩn thận
    // (Lỗi 422 rất hay xảy ra nếu gửi nhầm số thành chuỗi)
    const priceValue = parseFloat(document.getElementById('productPrice').value) || 0;
    
    // 2. Thu thập dữ liệu đầy đủ khớp 100% với Database của bạn
    const productData = {
        name: document.getElementById('productName').value,
        price: priceValue,
        description: document.getElementById('productDesc').value,
        image: imageUrl, // ĐÃ SỬA THÀNH 'image' THAY VÌ 'image_url'
        
        // Bơm thêm các trường cơ bản này vào để schemas.py không bị thiếu (có thể lấy từ form nếu web bạn có)
        category: "Sneaker", // Tạm để cứng nếu form chưa có ô chọn danh mục
        category_id: 1,      // Tạm để cứng
        brand: "Nike",       // Tạm để cứng
        color: "Chưa xác định",
        stock_quantity: 10,
        material: "Vải/Da",
        gender: "Unisex",
        season: "Hè",
        style: "Thể thao",
        is_active: true
    };

    try {
        // 3. Gọi API FastAPI
        const response = await fetch('http://localhost:8000/api/products', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(productData)
        });

        if (response.ok) {
            alert("Thêm sản phẩm thành công!");
            window.location.reload();
        } else {
            // NẾU VẪN LỖI, IN THẲNG LỖI RA MÀN HÌNH ĐỂ XEM
            const errorData = await response.json();
            console.error("Chi tiết lỗi 422 từ Backend:", errorData);
            alert("Lỗi Backend: " + JSON.stringify(errorData.detail));
        }
    } catch (err) {
        console.error("Lỗi khi fetch:", err);
        alert("Không thể kết nối đến máy chủ FastAPI!");
    }
}