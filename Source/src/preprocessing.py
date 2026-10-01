# -*- coding: utf-8 -*-
"""
IE403 - Khai thác Dữ liệu và Truyền thông Xã hội | UIT - ĐHQG-HCM
Đề tài: Hệ Thống Dự Báo Nguy Cơ Mưa Ngập Cục Bộ Khu Vực UIT & Thủ Đức Dựa Trên Quy Trình KDD
Bản quyền (C) 2026 Nguyễn Duy Nhiệm. Bảo lưu mọi quyền.
Tác giả: Nguyễn Duy Nhiệm (https://github.com/DuyNhiemUIT)
SPDX-License-Identifier: MIT
"""

"""
Module: preprocessing.py
Mục đích: Tiền xử lý dữ liệu khí tượng TP.HCM theo đúng chuẩn giáo trình môn học IE403:
1. Làm sạch dữ liệu (Data Cleaning: Missing values, Outliers).
2. Phân tích hệ số tương quan Pearson (r) phát hiện thuộc tính dư thừa.
3. Chuẩn hóa Min-Max và Z-Score.
4. Rời rạc hóa thuộc tính liên tục thành các biến định tính (Discretization).
5. Phân chia Train / Validation / Test (Stratified) chống Data Leakage.
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

PREDICTOR_NUM_COLS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "relative_humidity_2m_mean",
    "surface_pressure_mean",
    "wind_speed_10m_max",
    "wind_direction_10m_dominant",
    "dew_point_2m_mean"
]

TARGET_COL = "Rain_Flood_Risk"

def pearson_correlation_coefficient(x, y):
    """
    Tính hệ số tương quan tuyến tính Pearson r giữa hai thuộc tính số x và y:
    r = (xy_bar - x_bar * y_bar) / (sigma_x * sigma_y)
    (Đúng theo công thức slide Bài 1.2 - Tiền xử lý dữ liệu, slide 24-26)
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    if n == 0:
        return 0.0
    
    x_bar = np.mean(x)
    y_bar = np.mean(y)
    xy_bar = np.mean(x * y)
    
    sigma_x = np.std(x, ddof=0)
    sigma_y = np.std(y, ddof=0)
    
    if sigma_x == 0 or sigma_y == 0:
        return 0.0
        
    r = (xy_bar - (x_bar * y_bar)) / (sigma_x * sigma_y)
    return float(np.clip(r, -1.0, 1.0))

def compute_correlation_matrix(df, columns):
    """
    Tính ma trận tương quan Pearson giữa tất cả các cặp biến số.
    """
    matrix = pd.DataFrame(index=columns, columns=columns, dtype=float)
    for col1 in columns:
        for col2 in columns:
            matrix.loc[col1, col2] = pearson_correlation_coefficient(df[col1], df[col2])
    return matrix

def min_max_normalize(series, new_min=0.0, new_max=1.0):
    """
    Chuẩn hóa Min-Max (slide Bài 1.2, slide 36):
    v' = ((v - min) / (max - min)) * (new_max - new_min) + new_min
    """
    s_min = series.min()
    s_max = series.max()
    if s_max == s_min:
        return series * 0.0
    return ((series - s_min) / (s_max - s_min)) * (new_max - new_min) + new_min

def z_score_normalize(series):
    """
    Chuẩn hóa Z-Score (slide Bài 1.2, slide 37):
    v' = (v - mean) / sigma
    """
    mean = series.mean()
    std = series.std(ddof=0)
    if std == 0:
        return series * 0.0
    return (series - mean) / std

def discretize_hcmc_weather(df):
    """
    Rời rạc hóa các thuộc tính liên tục thành các khoảng ý niệm định tính
    để lập Hệ quyết định DS = (U, C U {d}) phục vụ lý thuyết Tập thô (Rough Set / Reduct)
    và Cây quyết định ID3 / Naive Bayes (theo slide Bài 3 & Bài 5).
    """
    disc_df = pd.DataFrame(index=df.index)
    disc_df["date"] = df["date"]
    
    # 1. Nhiệt độ trung bình: Lanh (<26), Mat (26-30), Nong (>30)
    disc_df["NhietDo"] = pd.cut(
        df["temperature_2m_mean"],
        bins=[-np.inf, 26.0, 30.0, np.inf],
        labels=["Lanh", "Mat", "Nong"]
    ).astype(str)
    
    # 2. Độ ẩm tương đối: BinhThuong (<75%), Cao (>=75%)
    disc_df["DoAm"] = pd.cut(
        df["relative_humidity_2m_mean"],
        bins=[-np.inf, 75.0, np.inf],
        labels=["BinhThuong", "Cao"]
    ).astype(str)
    
    # 3. Áp suất bề mặt: Thap (<1008 hPa), TB (1008-1012 hPa), Cao (>1012 hPa)
    disc_df["ApSuat"] = pd.cut(
        df["surface_pressure_mean"],
        bins=[-np.inf, 1008.0, 1012.0, np.inf],
        labels=["Thap", "TB", "Cao"]
    ).astype(str)
    
    # 4. Tốc độ gió: Yeu (<15 km/h), Manh (>=15 km/h)
    disc_df["Gio"] = pd.cut(
        df["wind_speed_10m_max"],
        bins=[-np.inf, 15.0, np.inf],
        labels=["Yeu", "Manh"]
    ).astype(str)
    
    # 5. Hướng gió: TayNam (180-270 độ, gió mùa ẩm gây ngập), DongBac (0-90 độ), Khac
    def categorize_wind_direction(deg):
        if 180.0 <= deg <= 270.0:
            return "TayNam"
        elif 0.0 <= deg <= 90.0 or deg >= 350.0:
            return "DongBac"
        else:
            return "Khac"
    disc_df["HuongGio"] = df["wind_direction_10m_dominant"].apply(categorize_wind_direction)
    
    # 6. Chênh lệch nhiệt độ ngày (Biên độ nhiệt: Hep <= 7 độ, Rong > 7 độ)
    temp_range = df["temperature_2m_max"] - df["temperature_2m_min"]
    disc_df["BienDoNhiet"] = np.where(temp_range > 7.0, "Rong", "Hep")
    
    # Nhãn quyết định
    disc_df[TARGET_COL] = df[TARGET_COL]
    return disc_df

def run_preprocessing_pipeline(raw_csv_path, processed_dir):
    """
    Thực thi trọn vẹn quy trình tiền xử lý:
    - Làm sạch dữ liệu
    - Phân tích tương quan Pearson
    - Rời rạc hóa
    - Chuẩn hóa Z-Score & Min-Max
    - Phân chia Stratified Train (60%), Validation (20%), Test (20%)
    """
    os.makedirs(processed_dir, exist_ok=True)
    df = pd.read_csv(raw_csv_path)
    logging.info(f"Đọc dữ liệu thô: {len(df)} dòng, {len(df.columns)} cột.")
    
    # 1. Làm sạch giá trị thiếu nếu có
    missing_count = df[PREDICTOR_NUM_COLS].isnull().sum().sum()
    if missing_count > 0:
        logging.warning(f"Phát hiện {missing_count} giá trị thiếu. Tiến hành điền bằng trung vị...")
        df[PREDICTOR_NUM_COLS] = df[PREDICTOR_NUM_COLS].fillna(df[PREDICTOR_NUM_COLS].median())
        
    # Loại bỏ bản ghi trùng
    df.drop_duplicates(subset=["date"], inplace=True)
    
    # 2. Phân tích tương quan Pearson
    corr_matrix = compute_correlation_matrix(df, PREDICTOR_NUM_COLS)
    corr_path = os.path.join(processed_dir, "pearson_correlation_matrix.csv")
    corr_matrix.to_csv(corr_path)
    logging.info(f"Đã lưu ma trận tương quan Pearson vào: {corr_path}")
    
    # 3. Rời rạc hóa cho bài toán Rough Set và Decision Tree ID3
    df_discrete = discretize_hcmc_weather(df)
    disc_path = os.path.join(processed_dir, "hcmc_weather_discrete.csv")
    df_discrete.to_csv(disc_path, index=False)
    logging.info(f"Đã lưu tập dữ liệu rời rạc hóa vào: {disc_path}")
    
    # 4. Chuẩn hóa số học (Min-Max và Z-Score)
    df_normalized = df.copy()
    for col in PREDICTOR_NUM_COLS:
        df_normalized[col + "_minmax"] = min_max_normalize(df[col])
        df_normalized[col + "_zscore"] = z_score_normalize(df[col])
    norm_path = os.path.join(processed_dir, "hcmc_weather_normalized.csv")
    df_normalized.to_csv(norm_path, index=False)
    logging.info(f"Đã lưu tập dữ liệu chuẩn hóa vào: {norm_path}")
    
    # 5. Phân chia Train/Validation/Test (Stratified theo nhãn Nguy cơ ngập)
    # 60% Train, 20% Val, 20% Test
    train_df, temp_df = train_test_split(
        df_discrete, test_size=0.4, random_state=42, stratify=df_discrete[TARGET_COL]
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.5, random_state=42, stratify=temp_df[TARGET_COL]
    )
    
    train_df.to_csv(os.path.join(processed_dir, "train_discrete.csv"), index=False)
    val_df.to_csv(os.path.join(processed_dir, "val_discrete.csv"), index=False)
    test_df.to_csv(os.path.join(processed_dir, "test_discrete.csv"), index=False)
    
    # Lưu metadata thông tin phân chia
    split_meta = {
        "total_samples": len(df_discrete),
        "train_samples": len(train_df),
        "val_samples": len(val_df),
        "test_samples": len(test_df),
        "train_flood_rate": float(train_df[TARGET_COL].mean()),
        "val_flood_rate": float(val_df[TARGET_COL].mean()),
        "test_flood_rate": float(test_df[TARGET_COL].mean()),
        "discrete_attributes": ["NhietDo", "DoAm", "ApSuat", "Gio", "HuongGio", "BienDoNhiet"],
        "target_attribute": TARGET_COL
    }
    with open(os.path.join(processed_dir, "dataset_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(split_meta, f, indent=4, ensure_ascii=False)
        
    logging.info(f"Phân chia hoàn tất: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}.")
    return split_meta

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    base_dir = os.path.dirname(os.path.dirname(__file__))
    raw_path = os.path.join(base_dir, "data", "raw", "hcmc_weather_2020_2026.csv")
    proc_dir = os.path.join(base_dir, "data", "processed")
    meta = run_preprocessing_pipeline(raw_path, proc_dir)
    print("Hoan tat tien xu ly! Metadata:")
    print(json.dumps(meta, indent=2))

if __name__ == "__main__":
    main()
