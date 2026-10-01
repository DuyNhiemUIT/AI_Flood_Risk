# 📚 TỪ ĐIỂN DỮ LIỆU KHÍ TƯỢNG VÀ NGUY CƠ MƯA NGẬP TP.HCM (DATA DICTIONARY)

> **DỰ ÁN:** HỆ THỐNG DỰ BÁO NGUY CƠ MƯA NGẬP CỤC BỘ KHU VỰC UIT & THỦ ĐỨC DỰA TRÊN QUY TRÌNH KDD  
> **ĐƠN VỊ:** KHOA HỆ THỐNG THÔNG TIN — TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN (UIT - ĐHQG-HCM)  
> **TÁC GIẢ:** NGUYỄN DUY NHIỆM (@DuyNhiemUIT)  
> **CỐ VẤN HỌC THUẬT:** ThS. MAI XUÂN HÙNG  
> **NGUỒN DỮ LIỆU:** ECMWF ERA5 Atmospheric Reanalysis (Tọa độ: 10.8231° N, 106.6297° E)  
> **QUY MÔ DỮ LIỆU:** 2.435 ngày quan trắc liên tục (01/01/2020 đến 31/08/2026)  

---

## 1. BẢNG DỮ LIỆU QUAN TRẮC ĐỊNH LƯỢNG THỰC TẾ (`hcmc_weather_raw`)

| Tên trường (Field) | Kiểu dữ liệu | Đơn vị | Ý nghĩa khoa học | Mô tả chi tiết |
| :--- | :---: | :---: | :--- | :--- |
| `date` | `DATE` / `TEXT` | YYYY-MM-DD | Ngày quan trắc | Khóa chính (Primary Key), 2.435 ngày liên tục |
| `temperature_2m_mean` | `FLOAT` | °C | Nhiệt độ trung bình ngày | Đo ở độ cao 2 mét tiêu chuẩn |
| `temperature_2m_max` | `FLOAT` | °C | Nhiệt độ cao nhất ngày | Đo lúc đỉnh điểm nhiệt |
| `temperature_2m_min` | `FLOAT` | °C | Nhiệt độ thấp nhất ngày | Đo lúc rạng sáng |
| `apparent_temperature_mean` | `FLOAT` | °C | Nhiệt độ cảm nhận trung bình | Nhiệt độ thực tế cơ thể người cảm nhận |
| `relative_humidity_2m_mean` | `FLOAT` | % | Độ ẩm tương đối trung bình | Yếu tố chỉ báo bão hòa hơi nước |
| `surface_pressure_mean` | `FLOAT` | hPa | Áp suất khí quyển bề mặt | Áp suất thấp (< 1008 hPa) chỉ báo nhiễu động dông |
| `wind_speed_10m_max` | `FLOAT` | km/h | Tốc độ gió giật cực đại | Đo ở độ cao 10 mét tiêu chuẩn WMO |
| `wind_direction_10m_dominant` | `INTEGER` | Độ (0-360°) | Hướng gió thịnh hành | Hướng gió thổi chủ đạo trong ngày |
| `precipitation_sum` | `FLOAT` | mm | Tổng lượng mưa ngày | Dùng để sinh nhãn giám sát (Bị cô lập khỏi feature train) |
| `Rain_Flood_Risk` | `INTEGER` | 0 hoặc 1 | Nhãn quyết định ngập úng | 1: Lượng mưa ≥ 50mm hoặc mưa lớn cực đoan; 0: Không ngập |

---

## 2. BẢNG THUỘC TÍNH RỜI RẠC HÓA PHỤC VỤ KHAI PHÁ KDD (`hcmc_weather_discrete`)

Toàn bộ 6 thuộc tính điều kiện liên tục đã được phân vùng rời rạc hóa thành các nhãn danh nghĩa (Nominal/Ordinal) phục vụ thuật toán Tập thô Pawlak và Cây quyết định:

| Thuộc tính rời rạc | Nhãn giá trị (Categories) | Ngưỡng chia (Cut-off Thresholds) | Ý nghĩa chuyên ngành khí tượng |
| :--- | :--- | :--- | :--- |
| `NhietDo` | `Thap`, `TrungBinh`, `Cao` | < 27.5°C; 27.5 - 29.5°C; > 29.5°C | Nền nhiệt đô thị TP.HCM |
| `DoAm` | `Thap`, `TrungBinh`, `Cao` | < 75%; 75% - 85%; > 85% | Độ ẩm cao báo hiệu mây đối lưu |
| `ApSuat` | `Thap`, `TrungBinh`, `Cao` | < 1008 hPa; 1008 - 1010.5 hPa; > 1010.5 hPa | Vùng rãnh áp thấp nhiệt đới |
| `Gio` | `Nhe`, `Vua`, `Manh` | < 10 km/h; 10 - 16 km/h; > 16 km/h | Tốc độ gió bề mặt |
| `HuongGio` | `DongBac`, `TayNam`, `Khac` | 0° - 90°; 180° - 270°; Còn lại | Gió mùa Tây Nam (mùa mưa) vs Gió mùa Đông Bắc |
| `BienDoNhiet` | `Hep`, `Rong` | < 7.0°C; ≥ 7.0°C | Chênh lệch nhiệt độ ngày và đêm |
| `Rain_Flood_Risk` | `0` (An toàn), `1` (Nguy cơ ngập) | Ngưỡng mưa 50mm | Thuộc tính quyết định (Decision Attribute) |

---

## 3. TỆP TIN CƠ SỞ DỮ LIỆU SQL ĐÍNH KÈM

Hệ thống cung cấp sẵn 2 bản phân phối SQL tương thích với các hệ quản trị CSDL phổ biến:
1. **`Data/hcmc_weather_kdd.sql` (372 KB):** Chuẩn cú pháp MySQL 8.0+ và MariaDB 10.x (InnoDB Engine, utf8mb4, comment tiếng Việt, chỉ mục index nội bộ).
2. **`Data/hcmc_weather_kdd_sqlite.sql` (553 KB):** Chuẩn ANSI SQL tương thích 100% với SQLite 3, PostgreSQL.
