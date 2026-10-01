# -*- coding: utf-8 -*-
"""
IE403 - Khai thác Dữ liệu và Truyền thông Xã hội | UIT - ĐHQG-HCM
Đề tài: Hệ Thống Dự Báo Nguy Cơ Mưa Ngập Cục Bộ Khu Vực UIT & Thủ Đức Dựa Trên Quy Trình KDD
Bản quyền (C) 2026 Nguyễn Duy Nhiệm. Bảo lưu mọi quyền.
Tác giả: Nguyễn Duy Nhiệm (https://github.com/DuyNhiemUIT)
SPDX-License-Identifier: MIT
"""

"""
Module: test_pipeline.py
Mục đích: Bộ kiểm thử tự động (Unit Tests) cho toàn bộ quy trình KDD của Đồ án môn học IE403:
- Kiểm tra dữ liệu thô và nhãn quyết định
- Kiểm tra tiền xử lý, tính toán tương quan Pearson và rời rạc hóa
- Kiểm tra lý thuyết tập thô (Rough Set & Reduct)
- Kiểm tra Cây quyết định ID3 và trích xuất luật
- Kiểm tra Naive Bayes có làm trơn Laplace
- Kiểm tra Gom cụm K-Means
- Kiểm tra tính toán Ma trận nhầm lẫn và Metric
"""

import os
import sys
import pytest
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from preprocessing import pearson_correlation_coefficient, discretize_hcmc_weather
from rough_set import RoughSetAnalyzer
from decision_tree import ID3DecisionTree
from naive_bayes import LaplaceNaiveBayes
from clustering import CustomKMeans
from evaluation import compute_confusion_matrix

def test_pearson_correlation():
    # Hai biến tỷ lệ thuận hoàn hảo
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    y = [2.0, 4.0, 6.0, 8.0, 10.0]
    r = pearson_correlation_coefficient(x, y)
    assert abs(r - 1.0) < 1e-4
    
    # Hai biến tỷ lệ nghịch hoàn hảo
    z = [10.0, 8.0, 6.0, 4.0, 2.0]
    r_inv = pearson_correlation_coefficient(x, z)
    assert abs(r_inv - (-1.0)) < 1e-4

def test_discretization():
    sample_data = {
        "date": ["2026-09-01", "2026-09-02"],
        "temperature_2m_mean": [25.0, 31.0],
        "relative_humidity_2m_mean": [80.0, 60.0],
        "surface_pressure_mean": [1005.0, 1015.0],
        "wind_speed_10m_max": [16.0, 10.0],
        "wind_direction_10m_dominant": [220.0, 45.0],
        "temperature_2m_max": [30.0, 34.0],
        "temperature_2m_min": [24.0, 25.0],
        "Rain_Flood_Risk": [1, 0]
    }
    df = pd.DataFrame(sample_data)
    df_disc = discretize_hcmc_weather(df)
    
    assert df_disc.loc[0, "NhietDo"] == "Lanh"
    assert df_disc.loc[1, "NhietDo"] == "Nong"
    assert df_disc.loc[0, "DoAm"] == "Cao"
    assert df_disc.loc[1, "DoAm"] == "BinhThuong"
    assert df_disc.loc[0, "HuongGio"] == "TayNam"
    assert df_disc.loc[1, "HuongGio"] == "DongBac"

def test_rough_set_theory():
    # Kiểm tra tính toán tập thô trên đồ thị nhỏ
    sample_data = {
        "Troi": ["Nang", "Nang", "Mua", "Mua"],
        "Gio": ["Yeu", "Manh", "Yeu", "Manh"],
        "KetQua": [0, 0, 1, 1]
    }
    df = pd.DataFrame(sample_data)
    analyzer = RoughSetAnalyzer(condition_attrs=["Troi", "Gio"], decision_attr="KetQua")
    
    k = analyzer.compute_dependency_degree(df, ["Troi"])
    assert k == 1.0  # Kết quả phụ thuộc hoàn toàn vào Trời
    
    rules = analyzer.extract_100_percent_rules(df, ["Troi"])
    assert len(rules) == 2
    assert all(r["accuracy"] == 1.0 for r in rules)

def test_id3_decision_tree():
    sample_data = {
        "Outlook": ["Sunny", "Sunny", "Overcast", "Rain", "Rain"],
        "Humidity": ["High", "High", "High", "High", "Normal"],
        "Play": [0, 0, 1, 1, 1]
    }
    df = pd.DataFrame(sample_data)
    id3 = ID3DecisionTree(max_depth=3)
    id3.fit(df[["Outlook", "Humidity"]], df["Play"])
    
    rules = id3.extract_rules()
    assert len(rules) > 0
    
    preds = id3.predict(df[["Outlook", "Humidity"]])
    assert len(preds) == len(df)

def test_naive_bayes_laplace():
    sample_data = {
        "Weather": ["Sunny", "Sunny", "Rain", "Rain", "Rain"],
        "Wind": ["Weak", "Strong", "Weak", "Strong", "Weak"],
        "Label": [0, 0, 1, 1, 1]
    }
    df = pd.DataFrame(sample_data)
    nb = LaplaceNaiveBayes(use_laplace=True)
    nb.fit(df[["Weather", "Wind"]], df["Label"])
    
    # Kiểm tra không có xác suất nào bị bằng 0 nhờ làm trơn Laplace
    for c in nb.classes:
        assert nb.class_priors[c] > 0
        for col in ["Weather", "Wind"]:
            for val in nb.feature_domains[col]:
                assert nb.feature_likelihoods[c][col][val] > 0

def test_custom_kmeans():
    np.random.seed(42)
    # Tạo 2 cụm điểm phân biệt rõ ràng
    cluster1 = np.random.normal(loc=[1.0, 1.0], scale=0.2, size=(20, 2))
    cluster2 = np.random.normal(loc=[5.0, 5.0], scale=0.2, size=(20, 2))
    X = np.vstack([cluster1, cluster2])
    
    kmeans = CustomKMeans(k=2, max_iter=50, random_state=42)
    kmeans.fit(X)
    
    assert kmeans.centroids.shape == (2, 2)
    # 2 cụm phải được tách biệt rõ
    assert len(np.unique(kmeans.labels_)) == 2

def test_evaluation_confusion_matrix():
    y_true = [1, 1, 0, 0]
    y_pred = [1, 0, 0, 1]
    # TP=1, FN=1, FP=1, TN=1
    cm = compute_confusion_matrix(y_true, y_pred)
    assert cm["TP"] == 1
    assert cm["FN"] == 1
    assert cm["FP"] == 1
    assert cm["TN"] == 1
    assert cm["Accuracy"] == 0.5
    assert cm["Precision"] == 0.5
    assert cm["Recall"] == 0.5
    assert cm["F1_Score"] == 0.5
