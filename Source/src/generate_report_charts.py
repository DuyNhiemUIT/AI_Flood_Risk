# -*- coding: utf-8 -*-
"""
IE403 - Khai thác Dữ liệu và Truyền thông Xã hội | UIT - ĐHQG-HCM
Đề tài: Hệ Thống Dự Báo Nguy Cơ Mưa Ngập Cục Bộ Khu Vực UIT & Thủ Đức Dựa Trên Quy Trình KDD
Bản quyền (C) 2026 Nguyễn Duy Nhiệm. Bảo lưu mọi quyền.
Tác giả: Nguyễn Duy Nhiệm (https://github.com/DuyNhiemUIT)
SPDX-License-Identifier: MIT
"""

"""
Script: generate_report_charts.py
Tạo các biểu đồ bổ trợ chuyên sâu cho Báo cáo Đồ án (Word) và Slide (PowerPoint):
1. Ma trận tương quan Pearson Heatmap (chuẩn hóa hiển thị đẹp mắt).
2. Phân bố nhãn ngập lụt theo tháng / mùa và phân chia dữ liệu Train/Val/Test.
3. Kiến trúc hệ thống Pipeline KDD.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(PROJECT_DIR, "outputs")
DATA_RAW_PATH = os.path.join(PROJECT_DIR, "data", "raw", "hcmc_weather_2020_2026.csv")

# Cấu hình font và style cho biểu đồ học thuật
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI']
plt.rcParams['axes.unicode_minus'] = False

def generate_pearson_heatmap():
    if not os.path.exists(DATA_RAW_PATH):
        print("Data raw not found!")
        return
    df = pd.read_csv(DATA_RAW_PATH)
    df['temp_range'] = df['temperature_2m_max'] - df['temperature_2m_min']
    
    feature_cols = [
        'temperature_2m_max', 'temperature_2m_min', 'temperature_2m_mean',
        'relative_humidity_2m_mean', 'surface_pressure_mean',
        'wind_speed_10m_max', 'wind_direction_10m_dominant',
        'temp_range', 'Rain_Flood_Risk'
    ]
    name_map = {
        'temperature_2m_max': 'Nhiệt độ Max (°C)',
        'temperature_2m_min': 'Nhiệt độ Min (°C)',
        'temperature_2m_mean': 'Nhiệt độ TB (°C)',
        'relative_humidity_2m_mean': 'Độ ẩm TB (%)',
        'surface_pressure_mean': 'Áp suất bề mặt (hPa)',
        'wind_speed_10m_max': 'Tốc độ gió Max (km/h)',
        'wind_direction_10m_dominant': 'Hướng gió chính (°)',
        'temp_range': 'Biên độ nhiệt (°C)',
        'Rain_Flood_Risk': 'Nguy cơ Ngập (d)'
    }
    
    sub_df = df[feature_cols].rename(columns=name_map)
    corr = sub_df.corr(method='pearson')
    
    plt.figure(figsize=(10, 8), dpi=300)
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='Blues', vmin=-1, vmax=1,
                square=True, linewidths=.5, cbar_kws={"shrink": .8})
    plt.title("Ma trận Hệ số Tương quan Tuyến tính Pearson (r)\ngiữa các yếu tố khí tượng và Nguy cơ Ngập lụt tại TP.HCM", fontsize=13, fontweight='bold', pad=15)
    plt.tight_layout()
    out_path = os.path.join(OUTPUTS_DIR, "pearson_correlation_heatmap.png")
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_path}")

def generate_flood_season_chart():
    df = pd.read_csv(DATA_RAW_PATH)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    
    monthly_flood = df.groupby('month')['Rain_Flood_Risk'].agg(['count', 'sum'])
    monthly_flood['rate'] = (monthly_flood['sum'] / monthly_flood['count']) * 100
    
    fig, ax1 = plt.subplots(figsize=(10, 5), dpi=300)
    
    months = [f"Thg {m}" for m in range(1, 13)]
    color1 = '#2980b9'
    color2 = '#c0392b'
    
    bars = ax1.bar(months, monthly_flood['sum'], color=color1, alpha=0.85, label='Số ngày mưa to ngập úng (ngày)')
    ax1.set_xlabel('Tháng trong năm (Giai đoạn 2020 - 2026)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Số ngày xảy ra ngập úng (ngày)', color=color1, fontsize=11, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    
    for bar in bars:
        yval = bar.get_height()
        if yval > 0:
            ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.8, int(yval), ha='center', va='bottom', fontsize=9, fontweight='bold', color=color1)
            
    ax2 = ax1.twinx()
    ax2.plot(months, monthly_flood['rate'], color=color2, marker='o', linewidth=2.5, label='Tỷ lệ ngập úng (%)')
    ax2.set_ylabel('Tỷ lệ ngập úng (%)', color=color2, fontsize=11, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(0, 35)
    
    for i, txt in enumerate(monthly_flood['rate']):
        ax2.annotate(f"{txt:.1f}%", (months[i], txt + 0.9), ha='center', fontsize=8, color=color2, fontweight='bold')
        
    plt.title("Thống kê Phân bố Nguy cơ Ngập úng theo 12 Tháng tại TP.HCM\n(Rõ nét hai mùa: Mùa khô Thg 12 - Thg 4, Mùa mưa Thg 5 - Thg 11)", fontsize=12, fontweight='bold', pad=15)
    fig.tight_layout()
    out_path = os.path.join(OUTPUTS_DIR, "flood_monthly_distribution.png")
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_path}")

def generate_pipeline_architecture_diagram():
    fig, ax = plt.subplots(figsize=(11, 4), dpi=300)
    ax.axis('off')
    
    boxes = [
        {"text": "1. THU THẬP DỮ LIỆU\nOpen-Meteo API\n(2.435 ngày TP.HCM)", "x": 0.08, "color": "#E3F2FD", "edge": "#1976D2"},
        {"text": "2. TIỀN XỬ LÝ\n- Pearson r (EDA)\n- Min-Max / Z-Score\n- Rời rạc hóa WMO\n- Stratified 60-20-20", "x": 0.31, "color": "#E8F5E9", "edge": "#388E3C"},
        {"text": "3. TẬP THÔ (ROUGH SET)\n- Quan hệ IND(B)\n- Xấp xỉ trên / dưới\n- Rút gọn Reduct\n- 66 luật chuẩn 100%", "x": 0.54, "color": "#FFF3E0", "edge": "#F57C00"},
        {"text": "4. PHÂN LỚP & GOM CỤM\n- ID3 (Gain) & CART (Gini)\n- Naive Bayes (+Laplace)\n- K-Means & Kohonen SOM", "x": 0.77, "color": "#F3E5F5", "edge": "#7B1FA2"},
        {"text": "5. WEB APP STREAMLIT\n- Dự báo Realtime\n- Cảnh báo điểm đen UIT\n- Trực quan hóa cây & luật", "x": 1.00, "color": "#FFEBEE", "edge": "#D32F2F"}
    ]
    
    for i, b in enumerate(boxes):
        ax.text(b["x"], 0.5, b["text"], ha='center', va='center', fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor=b["color"], edgecolor=b["edge"], linewidth=2))
        if i < len(boxes) - 1:
            ax.annotate('', xy=(boxes[i+1]["x"] - 0.085, 0.5), xytext=(b["x"] + 0.085, 0.5),
                        arrowprops=dict(facecolor='#37474F', edgecolor='#37474F', width=2, headwidth=7, headlength=6))
            
    ax.set_xlim(-0.04, 1.12)
    ax.set_ylim(0.2, 0.8)
    plt.title("Quy trình Pipeline Khai thác Dữ liệu Dự báo Mưa to Ngập úng TP.HCM", fontsize=12, fontweight='bold', pad=10)
    plt.tight_layout()
    out_path = os.path.join(OUTPUTS_DIR, "system_architecture_pipeline.png")
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_path}")

if __name__ == "__main__":
    generate_pearson_heatmap()
    generate_flood_season_chart()
    generate_pipeline_architecture_diagram()
