# ======================================================================
# ĐỒ ÁN MÔN HỌC IE403: KHAI THÁC DỮ LIỆU VÀ TRUYỀN THÔNG XÃ HỘI (UIT)
# BẢN QUYỀN (C) 2026 NGUYỄN DUY NHIỆM (@DuyNhiemUIT)
# ======================================================================
FROM python:3.12-slim

WORKDIR /app

# Cài đặt curl phục vụ kiểm tra trạng thái container
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt thư viện phụ thuộc
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn đồ án
COPY . .

EXPOSE 8501

# Kiểm tra trạng thái ứng dụng Streamlit
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Khởi chạy Streamlit ứng dụng
ENTRYPOINT ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
