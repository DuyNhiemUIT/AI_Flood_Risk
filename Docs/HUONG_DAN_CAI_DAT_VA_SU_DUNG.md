# 📖 HƯỚNG DẪN CÀI ĐẶT VÀ VẬN HÀNH HỆ THỐNG

> **DỰ ÁN:** HỆ THỐNG DỰ BÁO NGUY CƠ MƯA NGẬP CỤC BỘ KHU VỰC UIT & THỦ ĐỨC DỰA TRÊN QUY TRÌNH KDD  
> **ĐƠN VỊ:** KHOA HỆ THỐNG THÔNG TIN — TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN (UIT - ĐHQG-HCM)  
> **CỐ VẤN HỌC THUẬT:** ThS. MAI XUÂN HÙNG  
> **TÁC GIẢ:** NGUYỄN DUY NHIỆM (@DuyNhiemUIT)  

---

## 1. TRẢI NGHIỆM TRỰC TUYẾN (KHÔNG CẦN CÀI ĐẶT)

- **Ứng dụng Web trực tuyến:** [uit-flood.streamlit.app](https://uit-flood.streamlit.app/)
- Tương thích mượt mà trên tất cả trình duyệt hiện đại: Google Chrome, Apple Safari, Microsoft Edge, Mozilla Firefox trên máy tính để bàn, laptop, tablet và smartphone.

---

## 2. YÊU CẦU HỆ THỐNG (KHI CHẠY CỤC BỘ)

- **Hệ điều hành:** Windows 10/11, macOS 12+ (hỗ trợ cả Apple Silicon M1/M2/M3/M4 và Intel), hoặc các bản phân phối Linux phổ biến (Ubuntu 20.04+, Debian, Fedora, Arch).
- **Môi trường:** Python 3.10 trở lên (khuyến nghị Python 3.11 hoặc 3.12).
- **Bộ nhớ RAM:** Tối thiểu 1 GB RAM trống (ứng dụng vận hành chỉ tiêu tốn ~150 MB RAM).
- **Dung lượng ổ đĩa:** Trống tối thiểu 300 MB cho môi trường ảo và thư viện.

---

## 3. KHỞI CHẠY NHANH 1-CLICK TỰ ĐỘNG (KHUYẾN NGHỊ)

Hệ thống được trang bị bộ script khởi chạy tự động hóa với cơ chế **Tự phục hồi (Self-Healing)**:
- **Tự động tạo môi trường ảo `.venv`** để cách ly hoàn toàn thư viện.
- **Tự động cài đặt gói phụ thuộc** từ `requirements.txt` nếu máy chưa có.
- **Tự động dò cổng mạng (Port Failover)**: Chuyển đổi an toàn từ 8501 sang 8502 nếu phát hiện cổng bị chiếm dụng.
- **Tự động mở trình duyệt web** ngay khi ứng dụng sẵn sàng.

### Trên Windows (10 / 11):
Nhấp đúp chuột vào tệp: 👉 **`run_app.bat`**

### Trên macOS (Finder):
Nhấp đúp chuột vào tệp: 👉 **`run_mac.command`**

### Qua Terminal (macOS & Linux):
```bash
chmod +x run_app.sh
./run_app.sh
```

---

## 4. KHỞI CHẠY BẰNG DOCKER

Nếu máy tính của bạn đã cài đặt Docker và Docker Compose:
```bash
# Khởi chạy container ngầm
docker compose -f Source/docker-compose.yml up -d --build

# Xem log thực thi
docker compose -f Source/docker-compose.yml logs -f
```
Truy cập ứng dụng tại: `http://localhost:8501`.

---

## 5. CÀI ĐẶT VÀ CHẠY THỦ CÔNG (DÀNH CHO DEVELOPER)

```bash
# 1. Tạo môi trường ảo
python -m venv .venv

# 2. Kích hoạt môi trường ảo
# Trên Windows:
.venv\Scripts\activate
# Trên macOS / Linux:
source .venv/bin/activate

# 3. Nâng cấp pip và cài đặt thư viện
pip install --upgrade pip
pip install -r requirements.txt

# 4. Khởi chạy ứng dụng Streamlit
streamlit run Source/app/streamlit_app.py
```

---

## 6. XỬ LÝ SỰ CỐ THƯỜNG GẶP (TROUBLESHOOTING)

| Tình huống | Nguyên nhân | Hướng khắc phục |
| :--- | :--- | :--- |
| **`Chưa tìm thấy Python`** | Máy tính chưa cài đặt Python hoặc chưa gán vào PATH | Cài đặt Python 3.10+ từ [python.org](https://www.python.org/downloads/) và nhớ tích chọn **"Add python.exe to PATH"**. |
| **`error: externally-managed-environment`** | Cơ chế PEP 668 trên macOS Homebrew | Script `run_app.sh` đã tự động xử lý thông qua `.venv`. Nếu chạy thủ công, hãy kích hoạt `.venv` trước khi pip install. |
| **`Permission denied: ./run_app.sh`** | File script trên Unix chưa có quyền thực thi | Chạy lệnh `chmod +x run_app.sh` hoặc chạy trực tiếp bằng `bash run_app.sh`. |
| **`Port 8501 is already in use`** | Cổng 8501 đang bị ứng dụng khác chiếm | Script tự động chuyển sang cổng 8502. Nếu chạy thủ công: `streamlit run Source/app/streamlit_app.py --server.port 8502`. |
| **Mất kết nối Internet** | Không thể gọi API Open-Meteo | Hệ thống tự động kích hoạt cơ chế Fallback sử dụng dữ liệu trạm quan trắc dự phòng WMO an toàn. |

---

## 7. THÔNG TIN LIÊN HỆ & BẢN QUYỀN

- **Tác giả:** [Nguyễn Duy Nhiệm](https://github.com/DuyNhiemUIT) (@DuyNhiemUIT)
- **Repository:** [https://github.com/DuyNhiemUIT/AI_Flood_Risk](https://github.com/DuyNhiemUIT/AI_Flood_Risk)
- **Đơn vị:** Khoa Hệ thống Thông tin — Trường Đại học Công nghệ Thông tin (UIT – ĐHQG-HCM)
- **Giấy phép:** [MIT License](LICENSE)
