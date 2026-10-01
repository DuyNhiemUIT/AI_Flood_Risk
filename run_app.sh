#!/usr/bin/env bash

# ======================================================================
# SCRIPT KHỞI CHẠY DEMO DÀNH CHO MACOS & LINUX (TERMINAL)
# ĐỒ ÁN MÔN HỌC IE403: KHAI THÁC DỮ LIỆU VÀ TRUYỀN THÔNG XÃ HỘI
# TÁC GIẢ: NGUYỄN DUY NHIỆM (@DuyNhiemUIT)
# GIẢNG VIÊN HƯỚNG DẪN: ThS. MAI XUÂN HÙNG - TRƯỜNG ĐH CNTT (UIT)
# ======================================================================

# Chuyển thư mục làm việc về thư mục chứa script
cd "$(dirname "$0")"

# Tự động di chuyển vào Source nếu chạy từ thư mục gốc đồ án
if [ -d "Source" ]; then
    cd Source
fi

echo "======================================================================"
echo " 🌧️ HỆ THỐNG DỰ BÁO NGUY CƠ MƯA NGẬP CỤC BỘ KHU VỰC UIT & THỦ ĐỨC"
echo " 🎓 ĐỒ ÁN MÔN HỌC: IE403 - KHAI THÁC DỮ LIỆU VÀ TRUYỀN THÔNG XÃ HỘI"
echo " 👤 Tác giả: NGUYỄN DUY NHIỆM (@DuyNhiemUIT)"
echo " 👨‍🏫 Giảng viên hướng dẫn: ThS. Mai Xuân Hùng"
echo "======================================================================"
echo ""

# Kiểm tra file ứng dụng
if [ ! -f "app/streamlit_app.py" ]; then
    echo "❌ [LỖI] Không tìm thấy file app/streamlit_app.py!"
    echo "   Vui lòng kiểm tra lại cấu trúc thư mục đồ án."
    exit 1
fi

# 1. Phát hiện Python 3 (Kiểm tra theo thứ tự ưu tiên)
PYTHON_CMD=""
for candidate in python3 /opt/homebrew/bin/python3 /usr/local/bin/python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        if "$candidate" -c "import sys; assert sys.version_info >= (3, 8)" >/dev/null 2>&1; then
            PYTHON_CMD="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "======================================================================"
    echo "❌ [CẢNH BÁO] CHƯA TÌM THẤY PYTHON 3 TRÊN HỆ THỐNG!"
    echo "======================================================================"
    echo "Để khởi chạy demo, hệ thống cần cài đặt Python 3.10 trở lên."
    echo ""
    echo "HƯỚNG DẪN CÀI ĐẶT NHANH DÀNH CHO THẦY / CÔ:"
    echo "👉 macOS (Cài qua Homebrew):  brew install python"
    echo "👉 Ubuntu / Debian:           sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "👉 Hoặc tải bộ cài trực tiếp: https://www.python.org/downloads/"
    echo "======================================================================"
    exit 1
fi

echo "🔍 [1/3] Môi trường Python: $("$PYTHON_CMD" - version)"

# 2. Tự động tạo và kích hoạt Virtual Environment (.venv)
if [ ! -d ".venv" ]; then
    echo "💡 [1/3] Đang tự động khởi tạo môi trường ảo .venv để cách ly thư viện..."
    "$PYTHON_CMD" -m venv .venv
fi

if [ -f ".venv/bin/activate" ]; then
    echo "💡 [1/3] Kích hoạt môi trường ảo .venv..."
    source .venv/bin/activate
    PYTHON_EXEC="python"
else
    PYTHON_EXEC="$PYTHON_CMD"
fi

# 3. Kiểm tra và tự động cài đặt thư viện phụ thuộc
echo "🔍 [2/3] Kiểm tra các thư viện (Streamlit, Pandas, Scikit-learn, Joblib)..."
if ! "$PYTHON_EXEC" -c "import streamlit, pandas, sklearn, joblib, matplotlib" >/dev/null 2>&1; then
    echo ""
    echo "📦 [THÔNG BÁO] Phát hiện thiếu thư viện hoặc lần đầu khởi chạy!"
    echo "   Đang tự động tải và cài đặt các thư viện cần thiết từ requirements.txt..."
    echo "   (Quá trình này mất khoảng 1-2 phút tùy tốc độ mạng, vui lòng đợi...)"
    echo ""
    "$PYTHON_EXEC" -m pip install - upgrade pip - quiet
    "$PYTHON_EXEC" -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo ""
        echo "======================================================================"
        echo "❌ [LỖI] Cài đặt thư viện thất bại! Vui lòng kiểm tra kết nối Internet."
        echo "======================================================================"
        exit 1
    fi
    echo "✅ [✓] Đã cài đặt đầy đủ tất cả thư viện cần thiết!"
else
    echo "✅ [✓] Các thư viện đã sẵn sàng!"
fi

# 4. Kiểm tra xung đột cổng (Port) và tự động failover
APP_PORT=$("$PYTHON_EXEC" -c "import socket; p = next((x for x in (8501, 8502, 8503, 8504) if socket.socket.connect_ex(('127.0.0.1', x)) != 0), 8501); print(p)")

if [ "$APP_PORT" != "8501" ]; then
    echo "⚠️  [THÔNG BÁO] Cổng 8501 đang bận, tự động chuyển sang cổng $APP_PORT..."
fi

# 5. Khởi chạy Streamlit Web App
echo ""
echo "======================================================================"
echo "🚀 [3/3] Đang khởi chạy Streamlit Web App tại: http://localhost:$APP_PORT"
echo "🌐 Trình duyệt Web sẽ tự động mở giao diện ứng dụng."
echo "🛑 Nhấn tổ hợp phím Ctrl + C trong cửa sổ này khi muốn dừng Demo."
echo "======================================================================"
echo ""

"$PYTHON_EXEC" -m streamlit run app/streamlit_app.py - server.port "$APP_PORT" - server.headless false
