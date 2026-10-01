# 🌧️ Hệ Thống Dự Báo Nguy Cơ Mưa Ngập Cục Bộ Khu Vực UIT & Thủ Đức
## Khám Phá Tri Thức (KDD) & Trí Tuệ Nhân Tạo Dự Báo Thời Tiết

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://uit-flood.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-22%2F22%20passed-brightgreen.svg)]()

> 🌐 **Live Web Application:** [https://uit-flood.streamlit.app/](https://uit-flood.streamlit.app/)  
> 🏛️ **Đơn vị:** Khoa Hệ thống Thông tin — Trường Đại học Công nghệ Thông tin (UIT – ĐHQG-HCM)  
> 👤 **Tác giả:** [Nguyễn Duy Nhiệm](https://github.com/DuyNhiemUIT) (@DuyNhiemUIT)  
> 👨‍🏫 **Cố vấn học thuật:** ThS. Mai Xuân Hùng  

---

## 📖 GIỚI THIỆU ĐỀ TÀI

Dự án nghiên cứu và phát triển giải pháp ứng dụng quy trình **Khám phá Tri thức trong Cơ sở Dữ liệu (KDD - Knowledge Discovery in Databases)** để phân tích, khai phá và dự báo sớm nguy cơ xảy ra mưa to gây ngập úng cục bộ tại khu vực khuôn viên Trường Đại học Công nghệ Thông tin (UIT) và các tuyến đường trũng thấp trọng điểm tại TP. Thủ Đức, TP. Hồ Chí Minh.

Hệ thống kết hợp dữ liệu khí tượng tái phân tích toàn cầu **ECMWF ERA5** (2.435 ngày quan trắc liên tục từ 2020 đến 2026) với dữ liệu thời gian thực từ trạm đo vệ tinh thông qua **Open-Meteo Live API**.

### 🌟 Kiến Trúc Ứng Dụng Kép (Dual-Mode Architecture)

Ứng dụng Web Streamlit được thiết kế với 2 phân hệ chuyên biệt:
1. **🛡️ Cổng Giám Sát Ngập Dân Sự (Citizen Flood Portal):**
   - Giám sát thời gian thực với giao diện SCADA Neon Cyberpunk.
   - La bàn hoa tiêu SVG động xoay theo hướng gió thực tế.
   - Bản đồ số tương tác (GPS / DeckGL) giám sát 4 điểm đen ngập úng quanh UIT (*Đường Tô Ngọc Vân, Quốc lộ 13 Chân cầu Bình Triệu, Dốc Võ Văn Ngân, Chợ Thủ Đức / Đặng Thị Rành*).
   - Tiện ích tra cứu lộ trình di chuyển an toàn đến UIT (từ KTX Khu A, KTX Khu B, Ngã tư Thủ Đức, Suối Tiên).
   - Danh bạ đường dây nóng ứng cứu khẩn cấp (114, 115, CSGT, Cứu hộ giao thông).

2. **🔬 Báo Cáo & Phòng Nghiên Cứu KDD (Research Lab):**
   - Trực quan hóa toàn diện quy trình KDD 5 bước: *Thu thập (EDA) ➔ Tiền xử lý (K-Means/SOM) ➔ Rút gọn thuộc tính (Rough Set Pawlak) ➔ Khai phá & Đánh giá (Naive Bayes, ID3, CART) ➔ Dự báo thời gian thực*.
   - Trung tâm mô phỏng phân lớp học máy với thanh trượt ngưỡng kích hoạt cảnh báo (θ = 0.20 → 0.80).

---

## 📂 CẤU TRÚC MÃ NGUỒN REPOSITORY

```
AI_Flood_Risk/
├── 📁 Source/                                   # Mã nguồn chính của ứng dụng
│   ├── app/
│   │   └── streamlit_app.py                     # Giao diện chính Streamlit Dual-Mode
│   ├── src/                                     # Các module thuật toán KDD cốt lõi
│   │   ├── audit_project.py                     # Script kiểm định tự động chất lượng hệ thống
│   │   ├── rough_set.py                         # Lý thuyết tập thô Pawlak & Ma trận Skowron
│   │   ├── naive_bayes.py                       # Mô hình Champion Naive Bayes (+ Laplace)
│   │   ├── decision_tree.py                     # Cây quyết định ID3 & CART
│   │   ├── clustering.py                        # Gom cụm K-Means & Mạng Kohonen SOM
│   │   ├── preprocessing.py                     # Rời rạc hóa & Stratified Split 60-20-20
│   │   ├── evaluation.py                        # Đánh giá ma trận nhầm lẫn & đối soát
│   │   ├── generate_report_charts.py            # Sinh biểu đồ phân tích trực quan
│   │   └── fetch_data.py                        # Thu thập dữ liệu khí tượng Open-Meteo / ERA5
│   ├── models/                                  # Mô hình máy học đã huấn luyện (.pkl)
│   │   ├── champion_model.pkl                   # Mô hình tối ưu Naive Bayes
│   │   └── all_models_bundle.pkl                # Trọng số toàn bộ 6 mô hình so sánh
│   ├── outputs/                                 # Biểu đồ EDA, Confusion Matrix, Luật Pawlak
│   ├── data/                                    # Dữ liệu khí tượng phục vụ chạy cục bộ
│   │   ├── raw/hcmc_weather_2020_2026.csv       # 2.435 bản ghi định lượng thô
│   │   └── processed/                           # Dữ liệu sau chuẩn hóa và rời rạc hóa
│   ├── tests/                                   # 22 bài kiểm thử tự động (pytest + AppTest)
│   ├── scripts/                                 # Các script tiện ích hỗ trợ CSDL & biểu đồ
│   │   ├── export_sql_dataset.py                # Xuất CSDL SQL từ dữ liệu
│   │   └── generate_diagrams.py                 # Sinh sơ đồ kiến trúc hệ thống
│   ├── requirements.txt                         # Danh sách thư viện Python phụ thuộc
│   ├── Dockerfile & docker-compose.yml          # Cấu hình container Docker
│   ├── run_app.bat                              # Khởi chạy 1-Click trên Windows
│   ├── run_mac.command                          # Khởi chạy 1-Click trên macOS Finder
│   └── run_app.sh                               # Script bash chạy trên macOS / Linux Terminal
│
├── 📁 Data/                                     # Cơ sở dữ liệu SQL & Từ điển dữ liệu
│   ├── hcmc_weather_kdd.sql                     # Script CSDL SQL (MySQL / MariaDB)
│   ├── hcmc_weather_kdd_sqlite.sql              # Script CSDL SQL (SQLite / PostgreSQL)
│   └── DATA_DICTIONARY.md                       # Từ điển dữ liệu chi tiết các thuộc tính
│
├── 📁 Docs/                                     # Tài liệu hướng dẫn kỹ thuật
│   └── HUONG_DAN_CAI_DAT_VA_SU_DUNG.md          # Hướng dẫn chi tiết cài đặt và sử dụng
│
├── .streamlit/config.toml                       # Cấu hình Dark Mode cho Streamlit Cloud
├── requirements.txt                             # Dependencies tại gốc repo cho Cloud Build
├── streamlit_app.py                             # Entry Point tự động cho Streamlit Cloud
├── LICENSE                                      # Giấy phép mã nguồn mở MIT License
└── README.md                                    # Tài liệu giới thiệu dự án
```

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT VÀ VẬN HÀNH

### 🌟 Cách 1: Trải nghiệm Trực Tuyến (0 Cần Cài Đặt)
Truy cập ngay: 👉 **[https://uit-flood.streamlit.app/](https://uit-flood.streamlit.app/)**  
Ứng dụng hoạt động mượt mà trên mọi trình duyệt (Chrome, Safari, Edge, Firefox) trên máy tính, máy tính bảng và điện thoại di động.

### 💻 Cách 2: Chạy cục bộ trên Windows (1-Click)
1. Tải repository hoặc clone về máy tính:
   ```bash
   git clone https://github.com/DuyNhiemUIT/AI_Flood_Risk.git
   cd AI_Flood_Risk
   ```
2. Nhấp đúp chuột vào file: 👉 **`run_app.bat`** (ở thư mục gốc hoặc trong `Source/`).
   * *Script tự động kiểm tra Python, tạo môi trường ảo `.venv`, cài đặt thư viện cần thiết, xử lý cổng mạng và tự động mở trình duyệt tại `http://localhost:8501`.*

### 🍎 Cách 3: Chạy trên macOS & Linux
- **Trên macOS Finder (1-Click):** Nhấp đúp vào file 👉 **`run_mac.command`**.
- **Qua Terminal:**
  ```bash
  chmod +x run_app.sh
  ./run_app.sh
  ```
  *Script tự động giải quyết cơ chế PEP 668 trên macOS Sonoma/Sequoia, tạo `.venv` và khởi chạy.*

### 🐳 Cách 4: Chạy bằng Docker
```bash
docker compose -f Source/docker-compose.yml up --build
```
Truy cập ứng dụng tại `http://localhost:8501`.

---

## 🔬 KẾT QUẢ KHOA HỌC & ĐIỂM SÁNG PHƯƠNG PHÁP LUẬN KDD

1. **Nguyên tắc Chống rò rỉ dữ liệu (Anti-Leakage):** Lượng mưa thực tế bị cô lập 100% khỏi không gian đặc trưng huấn luyện; chỉ sử dụng 6 tham số khí quyển tiền triệu chứng (*Nhiệt độ, Độ ẩm, Áp suất, Tốc độ gió, Hướng gió, Biên độ nhiệt*).
2. **Lý thuyết Tập thô Pawlak:** Hệ số phụ thuộc $k = 43.26\%$, ma trận phân biệt Skowron chứng minh toàn bộ 6 thuộc tính đều là thuộc tính cốt lõi (Core Reduct) không thể lược bỏ, trích xuất bộ **66 luật quyết định** chắc chắn 100%.
3. **Gom cụm K-Means & Kohonen SOM:** Tách biệt 3 hình thái khí hậu: Cụm 0 (Dông bão, ngập 28.86%), Cụm 1 (Chuyển mùa, ngập 13.92%), Cụm 2 (Mùa khô, ngập 0.12%).
4. **Lật tẩy Nghịch lý Accuracy (Accuracy Paradox):** Cây quyết định CART đạt Accuracy ảo 87.68% nhưng Recall chỉ đạt 4.92% (bỏ sót 58/61 trận ngập). Mô hình Champion Naive Bayes (+ Laplace & Cost-Sensitive Tuning $	heta = 0.35$) đạt **Recall 80.33%** (vượt trội gấp 16.3 lần CART), bắt đúng 49/61 trận ngập trên tập Test độc lập.

---

## 🧪 KIỂM ĐỊNH CHẤT LƯỢNG MÃ NGUỒN (TEST SUITE)

```bash
# 1. Chạy 22 bài kiểm thử tự động (100% Passed)
pytest Source/tests/ -v

# 2. Chạy quy trình kiểm định toàn diện hệ thống
python Source/src/audit_project.py
```

---

## 📜 BẢN QUYỀN & GIẤY PHÉP

Dự án được phát hành theo giấy phép mã nguồn mở **[MIT License](LICENSE)**.  
Bản quyền © 2026 [Nguyễn Duy Nhiệm](https://github.com/DuyNhiemUIT) (@DuyNhiemUIT). Mọi đóng góp và trích dẫn khoa học xin vui lòng ghi rõ nguồn tác giả.
