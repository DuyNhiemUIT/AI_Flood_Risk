# -*- coding: utf-8 -*-
"""
HỆ THỐNG DỰ BÁO NGUY CƠ MƯA NGẬP CỤC BỘ KHU VỰC UIT & THỦ ĐỨC
Entry Point tự động cho Streamlit Community Cloud và môi trường production.
Chuyển tiếp thực thi mượt mà tới Source/app/streamlit_app.py.
"""

import os
import sys
import runpy

# Định vị đường dẫn ứng dụng
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_FILE = os.path.join(BASE_DIR, "Source", "app", "streamlit_app.py")

if not os.path.exists(APP_FILE):
    raise FileNotFoundError(f"Không tìm thấy file ứng dụng Streamlit tại: {APP_FILE}")

# Thực thi ứng dụng chính
runpy.run_path(APP_FILE, run_name="__main__")
