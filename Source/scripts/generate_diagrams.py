# -*- coding: utf-8 -*-
"""
Script: generate_diagrams.py
Tạo lại các sơ đồ kiến trúc chuẩn học thuật độ phân giải cao (300 DPI):
1. Hình 1.1: Sơ đồ kiến trúc tổng thể Pipeline Khai thác dữ liệu dự báo mưa ngập TP.HCM (system_architecture_pipeline.png)
2. Hình 5.1: Sơ đồ kiến trúc giao diện tương tác và các phân hệ chức năng trên Web App Streamlit (streamlit_app_interface.png)
"""

import os
import sys

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Cấu hình font chữ hỗ trợ tiếng Việt đầy đủ
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'Tahoma', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def draw_pipeline_architecture():
    fig = plt.figure(figsize=(16, 8.8), dpi=300)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8.8)
    ax.axis('off')

    # Nền tổng thể
    bg = FancyBboxPatch((0.1, 0.1), 15.8, 8.6, boxstyle="round,pad=0.08,rounding_size=0.15",
                        facecolor="#FAFBFC", edgecolor="#D0D7DE", linewidth=1.5, zorder=0)
    ax.add_patch(bg)

    # Header Banner
    header = FancyBboxPatch((0.3, 7.6), 15.4, 0.95, boxstyle="round,pad=0.06,rounding_size=0.12",
                            facecolor="#1B365D", edgecolor="#0F2038", linewidth=1.5, zorder=1)
    ax.add_patch(header)
    ax.text(8.0, 8.22, "SƠ ĐỒ KIẾN TRÚC TỔNG THỂ PIPELINE DỰ BÁO MƯA NGẬP TP.HCM (KDD PROCESS)",
            ha='center', va='center', fontsize=14, fontweight='bold', color='white', zorder=2)
    ax.text(8.0, 7.82, "Đồ án Môn học IE403: Khai thác dữ liệu và truyền thông xã hội | Sinh viên: Nguyễn Duy Nhiệm  - GVHD: ThS. Mai Xuân Hùng",
            ha='center', va='center', fontsize=10, color='#D4E6F1', zorder=2)

    # 5 Giai đoạn chính (5 Cột)
    stages = [
        {
            "step": "BƯỚC 1",
            "title": "THU THẬP & TÍCH HỢP\nDỮ LIỆU KHÍ TƯỢNG",
            "theme_bg": "#EBF5FB",
            "theme_border": "#2980B9",
            "badge_color": "#1B4F72",
            "x": 0.4,
            "width": 2.8,
            "items": [
                ("Nguồn Dữ Liệu:", True, "#1B4F72"),
                ("• Open-Meteo Historical API\n• ECMWF ERA5 Reanalysis", False, "#2C3E50"),
                ("Quy Mô & Thời Gian:", True, "#1B4F72"),
                ("• 2.435 ngày quan sát thực tế\n• Chuỗi 2020-01 đến 2026-08\n• Tọa độ TP.HCM: 10.82°N, 106.63°E", False, "#2C3E50"),
                ("Các Biến Khí Tượng Gốc:", True, "#1B4F72"),
                ("• Nhiệt độ (Max, Min, Mean)\n• Độ ẩm tương đối trung bình\n• Áp suất khí quyển bề mặt\n• Vận tốc & Hướng gió chủ đạo", False, "#2C3E50"),
                ("Nhãn Quyết Định (Proxy):", True, "#1B4F72"),
                ("• Rain_Flood_Risk (0 hoặc 1)\n• An toàn (0): 2.127 ngày (87.4%)\n• Nguy cơ ngập (1): 308 ngày (12.6%)", False, "#922B21")
            ]
        },
        {
            "step": "BƯỚC 2",
            "title": "TIỀN XỬ LÝ & KỸ NGHỆ\nĐẶC TRƯNG KHÍ HẬU",
            "theme_bg": "#E8F8F5",
            "theme_border": "#27AE60",
            "badge_color": "#145A32",
            "x": 3.5,
            "width": 2.8,
            "items": [
                ("Làm Sạch & Chuẩn Hóa:", True, "#145A32"),
                ("• Kiểm tra missing: 0 ô khuyết\n• Chuẩn hóa Min-Max Scaling [0,1]\n• Chuẩn hóa Z-score phân phối", False, "#2C3E50"),
                ("Phân Tích Tương Quan (EDA):", True, "#145A32"),
                ("• Ma trận hệ số Pearson (r)\n• Độ ẩm thuận mạnh: r = +0.42\n• Biên độ nhiệt nghịch: r = -0.38\n• Áp suất mặt đất: r = -0.22", False, "#2C3E50"),
                ("Rời Rạc Hóa Định Tính WMO:", True, "#145A32"),
                ("• Nhiệt độ: Lạnh, Mát, Nóng\n• Độ ẩm: BìnhThường, Cao (≥75%)\n• Áp suất: Thấp (<1008), TB, Cao\n• Hướng gió: TâyNam, ĐôngBắc", False, "#2C3E50"),
                ("Phân Hoạch Stratified Split:", True, "#145A32"),
                ("• Train Set: 1.461 ngày (60%)\n• Val Set: 487 ngày (20%)\n• Test Set: 487 ngày (20%)", False, "#196F3D")
            ]
        },
        {
            "step": "BƯỚC 3",
            "title": "KHAI PHÁ TẬP THÔ\n(ROUGH SET PAWLAK)",
            "theme_bg": "#FEF9E7",
            "theme_border": "#F39C12",
            "badge_color": "#7D6608",
            "x": 6.6,
            "width": 2.8,
            "items": [
                ("Quan Hệ Tương Đương IND:", True, "#7D6608"),
                ("• IND(C): 122 nhóm trạng thái thời tiết đặc trưng duy nhất", False, "#2C3E50"),
                ("Không Gian Xấp Xỉ Pawlak:", True, "#7D6608"),
                ("• Vùng dương POS_C(D): 632 ngày\n  - Hạ xấp xỉ Lớp 0: 627 ngày\n  - Hạ xấp xỉ Lớp 1: 5 ngày\n• Vùng biên BN_C(D): 829 ngày\n  (Tính bất định vi khí hậu đô thị)", False, "#2C3E50"),
                ("Hệ Số Phụ Thuộc Thuộc Tính:", True, "#7D6608"),
                ("• k = γ(C, D) = 632 / 1461 = 43.26%", False, "#B7950B"),
                ("Rút Gọn Ma Trận Skowron:", True, "#7D6608"),
                ("• 6/6 biến đều là Core Attributes\n• Reduct bảo toàn k = 43.26%\n• Trích xuất 66 luật IF-THEN\n  đạt độ tin cậy tuyệt đối 100.0%", False, "#B9770E")
            ]
        },
        {
            "step": "BƯỚC 4",
            "title": "MÔ HÌNH HỌC MÁY\n& ĐÁNH GIÁ ĐỐI SÁNH",
            "theme_bg": "#F4ECF7",
            "theme_border": "#8E44AD",
            "badge_color": "#512E5F",
            "x": 9.7,
            "width": 2.8,
            "items": [
                ("Cây Quyết Định (Decision Tree):", True, "#512E5F"),
                ("• ID3: Nút gốc DoAm (Gain=0.0937)\n  ApSuat (0.0705), BienDo (0.0621)\n• CART: Tối ưu Gini Index,\n  giới hạn max_depth=4 chống quá khớp", False, "#2C3E50"),
                ("Champion Model: Naive Bayes:", True, "#512E5F"),
                ("• Áp dụng kỹ thuật Laplace Smoothing\n• F1-Score cao nhất (0.4626)\n• Recall vượt trội: 55.74%\n  (Gấp 11.3 lần CART chỉ 4.92%)", False, "#922B21"),
                ("Tối Ưu Ngưỡng Phân Lớp (θ):", True, "#512E5F"),
                ("• Hạ ngưỡng θ = 0.50 -> θ = 0.35\n• Recall vọt lên 80.33% (bắt đúng 49/61 ngày ngập nguy hiểm)", False, "#7D3C98"),
                ("Học Không Giám Sát (Clustering):", True, "#512E5F"),
                ("• K-Means: K=3 cụm khí hậu\n• Kohonen SOM: Lưới nơ-ron 3×3", False, "#2C3E50")
            ]
        },
        {
            "step": "BƯỚC 5",
            "title": "TRIỂN KHAI WEB APP\n& HỖ TRỢ QUYẾT ĐỊNH",
            "theme_bg": "#FDEDEC",
            "theme_border": "#E74C3C",
            "badge_color": "#78281F",
            "x": 12.8,
            "width": 2.8,
            "items": [
                ("Kiến Trúc Web App Streamlit:", True, "#78281F"),
                ("• Dual-Mode Architecture:\n  Mode 1: Cổng Giám Sát UIT\n  Mode 2: Phòng Nghiên Cứu KDD", False, "#2C3E50"),
                ("Chức Năng Giám Sát Real-Time:", True, "#78281F"),
                ("• Tích hợp Live Weather API\n• Tính toán xác suất ngập tức thời\n• Tự động kích hoạt Báo Động Đỏ\n  khi P(d=1) ≥ Ngưỡng θ = 0.35", False, "#C0392B"),
                ("Hệ Thống 4 Điểm Đen Quanh UIT:", True, "#78281F"),
                ("• Bản đồ số Folium định vị:\n  1. Đường Tô Ngọc Vân\n  2. Chân cầu Bình Triệu QL13\n  3. Dốc Võ Văn Ngân\n  4. Đường Đặng Thị Rành", False, "#2C3E50"),
                ("Diễn Giải Mô Hình (XAI):", True, "#78281F"),
                ("• Minh bạch hóa 66 luật Pawlak\n• Khuyến nghị lộ trình tránh ngập", False, "#1B4F72")
            ]
        }
    ]

    for idx, s in enumerate(stages):
        x = s["x"]
        w = s["width"]
        y_top = 7.4
        box_h = 6.9
        y_bot = y_top - box_h

        # Hộp chứa từng cột giai đoạn
        stage_box = FancyBboxPatch((x, y_bot), w, box_h, boxstyle="round,pad=0.04,rounding_size=0.1",
                                   facecolor=s["theme_bg"], edgecolor=s["theme_border"], linewidth=1.5, zorder=1)
        ax.add_patch(stage_box)

        # Header Badge của cột
        badge_box = FancyBboxPatch((x + 0.15, y_top - 0.42), w - 0.3, 0.34, boxstyle="round,pad=0.03,rounding_size=0.08",
                                   facecolor=s["badge_color"], edgecolor=s["badge_color"], linewidth=1, zorder=2)
        ax.add_patch(badge_box)
        ax.text(x + w/2, y_top - 0.25, s["step"], ha='center', va='center',
                fontsize=9.5, fontweight='bold', color='white', zorder=3)

        # Title của cột
        ax.text(x + w/2, y_top - 0.75, s["title"], ha='center', va='center',
                fontsize=10, fontweight='bold', color=s["badge_color"], zorder=3, linespacing=1.15)

        # Đường kẻ phân cách dưới tiêu đề cột
        ax.plot([x + 0.2, x + w - 0.2], [y_top - 1.15, y_top - 1.15], color=s["theme_border"], linewidth=1, linestyle='-', zorder=2)

        # Nội dung chi tiết các mục
        cur_y = y_top - 1.35
        for header_text, is_bold, text_color in s["items"]:
            if is_bold:
                cur_y -= 0.08
                ax.text(x + 0.15, cur_y, header_text, ha='left', va='top',
                        fontsize=8.5, fontweight='bold', color=text_color, zorder=3)
                cur_y -= 0.22
            else:
                lines = header_text.split('\n')
                ax.text(x + 0.18, cur_y, header_text, ha='left', va='top',
                        fontsize=7.8, fontweight='normal', color=text_color, zorder=3, linespacing=1.2)
                cur_y -= len(lines) * 0.19 + 0.08

        # Mũi tên kết nối giữa các giai đoạn
        if idx < len(stages) - 1:
            arrow_x_start = x + w + 0.02
            arrow_x_end = stages[idx+1]["x"] - 0.02
            arrow_y = y_bot + box_h / 2
            ax.annotate('', xy=(arrow_x_end, arrow_y), xytext=(arrow_x_start, arrow_y),
                        arrowprops=dict(facecolor='#1B365D', edgecolor='#1B365D', width=2.5,
                                        headwidth=7.5, headlength=7.5, shrink=0.05), zorder=5)

    # Dải Footer ghi chú công nghệ
    footer_box = FancyBboxPatch((0.4, 0.22), 15.2, 0.45, boxstyle="round,pad=0.03,rounding_size=0.08",
                                facecolor="#FFFFFF", edgecolor="#B0BEC5", linewidth=1, zorder=2)
    ax.add_patch(footer_box)
    ax.text(8.0, 0.45, "Công nghệ nền tảng: Python 3.12 • Scikit-learn • Pawlak Rough Set • Naive Bayes (Laplace) • Decision Tree • Streamlit • Folium • Open-Meteo ERA5 API",
            ha='center', va='center', fontsize=9, fontweight='bold', color='#455A64', zorder=3)

    plt.tight_layout
    out_path = os.path.join(OUTPUTS_DIR, "system_architecture_pipeline.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close
    print("Da ve thanh cong Hinh 1.1 tai: " + str(out_path))

def draw_streamlit_interface_architecture():
    fig = plt.figure(figsize=(16, 11), dpi=300)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 11)
    ax.axis('off')

    # Nền tổng thể
    bg = FancyBboxPatch((0.1, 0.1), 15.8, 10.8, boxstyle="round,pad=0.08,rounding_size=0.15",
                        facecolor="#F4F6F9", edgecolor="#CFD8DC", linewidth=1.5, zorder=0)
    ax.add_patch(bg)

    # 1. Header Banner Ứng Dụng (Mô phỏng Giao diện Streamlit Top Bar)
    banner = FancyBboxPatch((0.4, 9.65), 15.2, 1.15, boxstyle="round,pad=0.06,rounding_size=0.12",
                            facecolor="#0B2545", edgecolor="#05162A", linewidth=1.5, zorder=1)
    ax.add_patch(banner)
    ax.text(8.0, 10.45, "HỆ THỐNG DỰ BÁO NGUY CƠ MƯA NGẬP CỤC BỘ KHU VỰC UIT & THỦ ĐỨC",
            ha='center', va='center', fontsize=14, fontweight='bold', color='white', zorder=2)
    ax.text(8.0, 10.05, "Đồ án Môn học IE403: Khai thác dữ liệu và truyền thông xã hội | Giảng viên hướng dẫn: ThS. Mai Xuân Hùng",
            ha='center', va='center', fontsize=10, color='#90CAF9', zorder=2)
    ax.text(8.0, 9.78, "Tác giả sinh viên: NGUYỄN DUY NHIỆM  - Khoa Hệ thống Thông tin - ĐHQG-HCM",
            ha='center', va='center', fontsize=9, color='#CFD8DC', zorder=2)

    # 2. Dual-Mode Selector Bar (Bộ chuyển đổi Chế độ kép)
    mode1_btn = FancyBboxPatch((0.4, 8.85), 7.45, 0.65, boxstyle="round,pad=0.04,rounding_size=0.08",
                               facecolor="#0284C7", edgecolor="#0369A1", linewidth=1.5, zorder=2)
    ax.add_patch(mode1_btn)
    ax.text(4.125, 9.18, "[CHẾ ĐỘ 1] CỔNG GIÁM SÁT NGẬP UIT & THỦ ĐỨC (Dành cho Sinh viên & Người dân)",
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='white', zorder=3)

    mode2_btn = FancyBboxPatch((8.15, 8.85), 7.45, 0.65, boxstyle="round,pad=0.04,rounding_size=0.08",
                               facecolor="#0D9488", edgecolor="#0F766E", linewidth=1.5, zorder=2)
    ax.add_patch(mode2_btn)
    ax.text(11.875, 9.18, "[CHẾ ĐỘ 2] BÁO CÁO & PHÒNG NGHIÊN CỨU KDD (Dành cho GV & Chuyên gia)",
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='white', zorder=3)

    # =========================================================================
    # KHUNG TRÁI: CHI TIẾT PHÂN HỆ 1 (PORTAL GIÁM SÁT REALTIME & CẢNH BÁO UIT)
    # =========================================================================
    p1_box = FancyBboxPatch((0.4, 0.8), 7.45, 7.85, boxstyle="round,pad=0.06,rounding_size=0.12",
                            facecolor="#FFFFFF", edgecolor="#0284C7", linewidth=2.0, zorder=1)
    ax.add_patch(p1_box)

    # Tiêu đề Khung Trái
    p1_title_box = FancyBboxPatch((0.6, 8.15), 7.05, 0.42, boxstyle="round,pad=0.03,rounding_size=0.06",
                                  facecolor="#E0F2FE", edgecolor="#0284C7", linewidth=1, zorder=2)
    ax.add_patch(p1_title_box)
    ax.text(4.125, 8.36, "PHÂN HỆ 1: GIÁM SÁT THỜI GIAN THỰC & CẢNH BÁO ĐIỂM ĐEN UIT",
            ha='center', va='center', fontsize=10.5, fontweight='bold', color="#0369A1", zorder=3)

    # 1.1 Khối Widget Thời Tiết Live API
    w_box = FancyBboxPatch((0.65, 6.95), 6.95, 1.05, boxstyle="round,pad=0.04,rounding_size=0.08",
                           facecolor="#F0F9FF", edgecolor="#BAE6FD", linewidth=1, zorder=2)
    ax.add_patch(w_box)
    ax.text(0.85, 7.8, "[LIVE API] Quan Trắc Khí Tượng Trực Tiếp (Open-Meteo TP.HCM):", fontsize=9, fontweight='bold', color="#0369A1", zorder=3)
    ax.text(0.85, 7.5, "• Nhiệt độ: 25.8°C (Mát)\n• Độ ẩm: 88.5% (Cao)", fontsize=8.5, color="#1E293B", zorder=3)
    ax.text(3.1, 7.5, "• Áp suất: 1006.2 hPa (Thấp)\n• Biên độ nhiệt: 5.2°C (Hẹp)", fontsize=8.5, color="#1E293B", zorder=3)
    ax.text(5.4, 7.5, "• Gió: 18.5 km/h (Mạnh)\n• Hướng gió: Tây Nam (Ẩm)", fontsize=8.5, color="#1E293B", zorder=3)

    # 1.2 Khối Cảnh Báo Nguy Cơ Ngập (Alert Card)
    alert_box = FancyBboxPatch((0.65, 5.55), 6.95, 1.25, boxstyle="round,pad=0.04,rounding_size=0.08",
                               facecolor="#FEF2F2", edgecolor="#EF4444", linewidth=2, zorder=2)
    ax.add_patch(alert_box)
    ax.text(0.85, 6.55, "[TRẠNG THÁI CẢNH BÁO] CHAMPION MODEL NAIVE BAYES:", fontsize=9.5, fontweight='bold', color="#B91C1C", zorder=3)
    ax.text(0.85, 6.22, "Xác suất ngập tính toán P(d = 1):", fontsize=9, color="#7F1D1D", zorder=3)
    ax.text(3.9, 6.22, "61.23% (NGUY CƠ NGẬP RẤT CAO)", fontsize=10, fontweight='bold', color="#DC2626", zorder=3)
    ax.text(0.85, 5.92, "Ngưỡng kích hoạt cảnh báo (Cost-Sensitive):", fontsize=8.5, color="#7F1D1D", zorder=3)
    ax.text(4.4, 5.92, "θ = 0.35 (Tối ưu Recall = 80.33%)", fontsize=9, fontweight='bold', color="#B91C1C", zorder=3)
    ax.text(0.85, 5.67, ">> KẾT LUẬN: BẬT BÁO ĐỘNG ĐỎ - NGUY CƠ NGẬP CỤC BỘ TRONG 1-3 GIỜ TỚI", fontsize=8.5, fontweight='bold', color="#991B1B", zorder=3)

    # 1.3 Khối 4 Điểm Đen Ngập Úng Quanh UIT
    hot_box = FancyBboxPatch((0.65, 2.75), 6.95, 2.65, boxstyle="round,pad=0.04,rounding_size=0.08",
                            facecolor="#F8FAFC", edgecolor="#CBD5E1", linewidth=1, zorder=2)
    ax.add_patch(hot_box)
    ax.text(0.85, 5.2, "[ĐIỂM ĐEN NGẬP] Giám Sát Chi Tiết 4 Trọng Điểm Khu Vực UIT & Thủ Đức:", fontsize=9, fontweight='bold', color="#0F172A", zorder=3)

    hotspots = [
        ("1. Đường Tô Ngọc Vân (Chợ Thủ Đức)", "Độ sâu: 0.5 - 0.7m", "Vùng trũng dâng nhanh, ngập qua ray xe lửa, chết máy cực cao", "Né nút Chợ Thủ Đức; đi Phạm Văn Đồng -> Đường số 6"),
        ("2. Quốc lộ 13 (Chân cầu Bình Triệu)", "Độ sâu: 0.4 - 0.6m", "Tê liệt cửa ngõ Đông Bắc, ngập cả 2 làn xe máy và ô tô", "Đi Phạm Văn Đồng -> Cầu Bình Lợi -> Quốc lộ 1A -> UIT"),
        ("3. Dốc Võ Văn Ngân (Nhà Thiếu Nhi)", "Độ sâu: 0.3 - 0.5m", "Độ dốc lớn tạo dòng nước xiết nguy hiểm, dễ cuốn ngã xe máy", "Đi Song hành Xa Lộ Hà Nội -> Lê Văn Việt -> Đặng Văn Bi"),
        ("4. Đường Đặng Thị Rành (Chợ Thủ Đức)", "Độ sâu: 0.3 - 0.4m", "Khu chợ cao độ thấp, nước ứ đọng do triều cường sông Sài Gòn", "Đi đường Thống Nhất hoặc Chu Mạnh Trinh kết nối Võ Văn Ngân")
    ]
    cur_hy = 4.88
    for name, depth, danger, avoid in hotspots:
        ax.text(0.85, cur_hy, f"• {name} | {depth}", fontsize=8.2, fontweight='bold', color="#C2410C", zorder=3)
        cur_hy -= 0.17
        ax.text(1.05, cur_hy, f"Nguy cơ: {danger}", fontsize=7.5, color="#334155", zorder=3)
        cur_hy -= 0.16
        ax.text(1.05, cur_hy, f"Lộ trình khuyến nghị: {avoid}", fontsize=7.5, fontstyle='italic', color="#0369A1", zorder=3)
        cur_hy -= 0.22

    # 1.4 Khối Bản Đồ Tương Tác Folium Map
    map_box = FancyBboxPatch((0.65, 0.95), 6.95, 1.65, boxstyle="round,pad=0.04,rounding_size=0.08",
                            facecolor="#ECFDF5", edgecolor="#A7F3D0", linewidth=1, zorder=2)
    ax.add_patch(map_box)
    ax.text(0.85, 2.4, "[BẢN ĐỒ SỐ] Trực Quan Hóa Không Gian Địa Lý (Interactive Folium Map):", fontsize=9, fontweight='bold', color="#065F46", zorder=3)
    ax.text(0.85, 2.1, "• Tích hợp bản đồ OpenStreetMap với Marker trực quan màu Đỏ / Cam / Vàng theo độ sâu ngập.", fontsize=8.0, color="#1E293B", zorder=3)
    ax.text(0.85, 1.85, "• Bán kính vòng tròn bán tự động quét vùng ảnh hưởng ngập xung quanh khuôn viên Trường ĐH CNTT (UIT).", fontsize=8.0, color="#1E293B", zorder=3)
    ax.text(0.85, 1.6, "• Popup cung cấp số điện thoại cứu hộ khẩn cấp, đường dây nóng Đội hỗ trợ sinh viên UIT khi xe chết máy.", fontsize=8.0, color="#1E293B", zorder=3)
    ax.text(0.85, 1.35, "• Tự động vẽ lộ trình vòng tránh ngập thông minh hướng dẫn sinh viên lưu thông an toàn về KTX Khu A & B.", fontsize=8.0, color="#1E293B", zorder=3)
    ax.text(0.85, 1.1, "• Người dùng có thể click trực tiếp vào từng điểm đen để xem lịch sử ngập 5 năm gần nhất.", fontsize=8.0, fontstyle='italic', color="#047857", zorder=3)

    # =========================================================================
    # KHUNG PHẢI: CHI TIẾT PHÂN HỆ 2 (BÁO CÁO & PHÒNG NGHIÊN CỨU KDD - 5 TABS)
    # =========================================================================
    p2_box = FancyBboxPatch((8.15, 0.8), 7.45, 7.85, boxstyle="round,pad=0.06,rounding_size=0.12",
                            facecolor="#FFFFFF", edgecolor="#0D9488", linewidth=2.0, zorder=1)
    ax.add_patch(p2_box)

    # Tiêu đề Khung Phải
    p2_title_box = FancyBboxPatch((8.35, 8.15), 7.05, 0.42, boxstyle="round,pad=0.03,rounding_size=0.06",
                                  facecolor="#CCFBF1", edgecolor="#0D9488", linewidth=1, zorder=2)
    ax.add_patch(p2_title_box)
    ax.text(11.875, 8.36, "PHÂN HỆ 2: BÁO CÁO & PHÒNG NGHIÊN CỨU KDD (5 CHUYÊN ĐỀ HỌC THUẬT)",
            ha='center', va='center', fontsize=10.5, fontweight='bold', color="#0F766E", zorder=3)

    # 5 Tab nghiên cứu chuyên sâu
    tabs = [
        {
            "id": "TAB 1",
            "name": "Khám Phá Dữ Liệu Khí Tượng (EDA)",
            "color": "#0369A1",
            "bg": "#F0F9FF",
            "border": "#BAE6FD",
            "content": [
                "• Trực quan hóa 2.435 ngày dữ liệu ECMWF ERA5 (2020-2026) tại TP.HCM.",
                "• Ma trận nhiệt Pearson: Độ ẩm r = +0.42 (thuận), Biên độ nhiệt r = -0.38 (nghịch).",
                "• Biểu đồ phân bố 12 tháng: Mùa mưa Thg 5-11 ngập 27-31%; Mùa khô Thg 12-4 ngập <3%."
            ]
        },
        {
            "id": "TAB 2",
            "name": "Tiền Xử Lý & Gom Cụm Khí Hậu (Clustering)",
            "color": "#15803D",
            "bg": "#F0FDF4",
            "border": "#BBF7D0",
            "content": [
                "• Rời rạc hóa chuẩn WMO: 6 thuộc tính điều kiện (Nhiệt độ, Độ ẩm, Áp suất, Hướng gió...).",
                "• Thuật toán K-Means (K = 3): Cụm 0 (Dông ngập 28.86%), Cụm 1 (Chuyển mùa 13.92%), Cụm 2 (Khô 0.12%).",
                "• Lưới nơ-ron tự tổ chức Kohonen SOM (3×3) phân bố không gian mẫu khí hậu rõ nét."
            ]
        },
        {
            "id": "TAB 3",
            "name": "Rút Gọn Tập Thô Pawlak & Diễn Giải Luật (XAI)",
            "color": "#B45309",
            "bg": "#FFFBEB",
            "border": "#FDE68A",
            "content": [
                "• Thiết lập quan hệ IND(C): Phân hoạch thành 122 nhóm trạng thái thời tiết duy nhất.",
                "• Vùng dương POS(D) = 632 ngày, Vùng biên BN(D) = 829 ngày -> Độ phụ thuộc k = 43.26%.",
                "• Rút gọn Skowron: 6 thuộc tính đều là Core Attributes. Trích xuất 66 luật tin cậy 100%."
            ]
        },
        {
            "id": "TAB 4",
            "name": "Đánh Giá Hiệu Năng & Đối Sánh Mô Hình (Test Set)",
            "color": "#7E22CE",
            "bg": "#FAF5FF",
            "border": "#E9D5FF",
            "content": [
                "• Đánh giá khách quan trên tập Test 487 ngày: ID3, CART, Naive Bayes (+Laplace).",
                "• Giải mã Nghịch lý Accuracy: CART Acc=87.68% nhưng Recall chỉ 4.92% (bỏ sót 58 ca ngập!).",
                "• Naive Bayes Champion Model: F1=0.4626, Recall=55.74%. Chỉnh θ=0.35 -> Recall=80.33%."
            ]
        },
        {
            "id": "TAB 5",
            "name": "Dự Báo Tương Tác & Thử Nghiệm Tùy Biến (Simulation)",
            "color": "#BE123C",
            "bg": "#FFF1F2",
            "border": "#FECDD3",
            "content": [
                "• Bảng điều khiển tương tác (Interactive Sliders): Tùy chỉnh nhiệt độ, độ ẩm, áp suất, gió...",
                "• Suy luận xác suất ngập theo thời gian thực kết hợp diễn giải cây quyết định CART.",
                "• Kiểm định chuỗi thời gian liên tục (Temporal Split) đánh giá khả năng chống Concept Drift."
            ]
        }
    ]

    cur_ty = 7.95
    for t in tabs:
        t_box = FancyBboxPatch((8.35, cur_ty - 1.25), 7.05, 1.28, boxstyle="round,pad=0.03,rounding_size=0.06",
                               facecolor=t["bg"], edgecolor=t["border"], linewidth=1.2, zorder=2)
        ax.add_patch(t_box)

        # Tab Badge & Tiêu đề
        badge = FancyBboxPatch((8.5, cur_ty - 0.28), 0.95, 0.24, boxstyle="round,pad=0.02,rounding_size=0.05",
                               facecolor=t["color"], edgecolor=t["color"], linewidth=1, zorder=3)
        ax.add_patch(badge)
        ax.text(8.975, cur_ty - 0.16, t["id"], ha='center', va='center', fontsize=8.0, fontweight='bold', color='white', zorder=4)

        ax.text(9.55, cur_ty - 0.16, t["name"], ha='left', va='center', fontsize=8.8, fontweight='bold', color=t["color"], zorder=3)

        # Nội dung của Tab
        line_y = cur_ty - 0.42
        for line in t["content"]:
            ax.text(8.55, line_y, line, ha='left', va='top', fontsize=7.6, color="#1E293B", zorder=3)
            line_y -= 0.24

        cur_ty -= 1.4

    # Footer Thanh điều khiển
    footer_bar = FancyBboxPatch((0.4, 0.2), 15.2, 0.45, boxstyle="round,pad=0.03,rounding_size=0.08",
                                facecolor="#FFFFFF", edgecolor="#B0BEC5", linewidth=1, zorder=2)
    ax.add_patch(footer_bar)
    ax.text(8.0, 0.42, "Cơ chế vận hành: Real-time Weather Ingestion -> Feature Discretization -> Pawlak Rule Engine -> Cost-Sensitive Classifier (θ=0.35) -> Folium Hotspot Map",
            ha='center', va='center', fontsize=8.8, fontweight='bold', color='#37474F', zorder=3)

    plt.tight_layout
    out_path = os.path.join(OUTPUTS_DIR, "streamlit_app_interface.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close
    print("Đã vẽ thành công Hình 5.1 tại: " + str(out_path))

if __name__ == "__main__":
    draw_pipeline_architecture
    draw_streamlit_interface_architecture
