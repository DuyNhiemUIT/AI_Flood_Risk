# -*- coding: utf-8 -*-
"""
IE403 - Khai thác Dữ liệu và Truyền thông Xã hội | UIT - ĐHQG-HCM
Đề tài: Hệ Thống Dự Báo Nguy Cơ Mưa Ngập Cục Bộ Khu Vực UIT & Thủ Đức Dựa Trên Quy Trình KDD
Bản quyền (C) 2026 Nguyễn Duy Nhiệm. Bảo lưu mọi quyền.
Tác giả: Nguyễn Duy Nhiệm (https://github.com/DuyNhiemUIT)
SPDX-License-Identifier: MIT
"""

"""
Module: evaluation.py
Mục đích: Đánh giá hiệu suất mô hình phân loại theo đúng bài giảng Bài 7 (Thầy Mai Xuân Hùng - UIT):
1. Ma trận nhầm lẫn (Confusion Matrix): TP, FN, FP, TN.
2. Bộ chỉ số: Accuracy, Precision, Recall, F1-Score.
3. So sánh mô hình trên tập Validation và tập Test độc lập.
4. Xuất bảng so sánh tổng hợp và biểu đồ trực quan.
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def compute_confusion_matrix(y_true, y_pred):
    """
    Tính toán các giá trị trong Ma trận nhầm lẫn:
    - TP: Thực tế Dương (1), Dự đoán Dương (1)
    - FN: Thực tế Dương (1), Dự đoán Âm (0)
    - FP: Thực tế Âm (0), Dự đoán Dương (1)
    - TN: Thực tế Âm (0), Dự đoán Âm (0)
    (Đúng theo slide Bài 7, slide 5-6)
    """
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    
    total = tp + fn + fp + tn
    accuracy = (tp + tn) / total if total > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "TP": tp,
        "FN": fn,
        "FP": fp,
        "TN": tn,
        "Total": total,
        "Accuracy": round(float(accuracy), 4),
        "Precision": round(float(precision), 4),
        "Recall": round(float(recall), 4),
        "F1_Score": round(float(f1), 4)
    }

def evaluate_models_on_dataset(models_dict, X_df, y_true, dataset_name="Validation"):
    """
    Đánh giá đồng thời danh sách các mô hình trên một tập dữ liệu (Val hoặc Test).
    """
    results = {}
    for model_name, model_info in models_dict.items():
        model = model_info["model"]
        features = model_info["features"]
        
        # Dự đoán
        if hasattr(model, "predict_one"):
            # ID3 hoặc Custom Naive Bayes
            preds = model.predict(X_df[features])
        elif hasattr(model, "predict"):
            # Scikit-learn (cần get_dummies)
            encoded_cols = model_info.get("encoded_cols", None)
            if encoded_cols:
                X_enc = pd.get_dummies(X_df[features], drop_first=False).reindex(columns=encoded_cols, fill_value=0)
                preds = model.predict(X_enc)
            else:
                preds = model.predict(X_df[features])
        else:
            raise ValueError(f"Mô hình {model_name} không hỗ trợ predict!")
            
        metrics = compute_confusion_matrix(y_true, preds)
        results[model_name] = metrics
        logging.info(f"[{dataset_name}] {model_name}: Acc={metrics['Accuracy']:.4f}, Prec={metrics['Precision']:.4f}, Rec={metrics['Recall']:.4f}, F1={metrics['F1_Score']:.4f}")
        
    return results

def plot_model_comparison(val_results, test_results, output_dir):
    """
    Vẽ biểu đồ cột so sánh Accuracy, Precision, Recall và F1-Score của các mô hình.
    """
    os.makedirs(output_dir, exist_ok=True)
    model_names = list(test_results.keys())
    metrics_keys = ["Accuracy", "Precision", "Recall", "F1_Score"]
    
    x = np.arange(len(model_names))
    width = 0.2
    
    fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
    colors = ["#4575b4", "#74add1", "#f46d43", "#d73027"]
    
    for i, m_key in enumerate(metrics_keys):
        vals = [test_results[m][m_key] for m in model_names]
        ax.bar(x + i * width, vals, width, label=m_key, color=colors[i])
        
    ax.set_title("So Sánh Hiệu Suất Các Mô Hình Trên Tập Kiểm Thử Độc Lập (Test Set)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(model_names, rotation=15, ha="right", fontsize=10)
    ax.set_ylim(0.0, 1.05)
    ax.set_ylabel("Giá trị Điểm số (0 - 1.0)", fontsize=11)
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    ax.legend(loc="lower right", framealpha=0.9)
    
    chart_path = os.path.join(output_dir, "model_comparison_test.png")
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    logging.info(f"Đã lưu biểu đồ so sánh mô hình vào: {chart_path}")
    return chart_path

def plot_confusion_matrix_grid(test_results, output_dir):
    """
    Vẽ ma trận nhầm lẫn trực quan cho từng mô hình.
    """
    fig, axes = plt.subplots(1, len(test_results), figsize=(4.5 * len(test_results), 4), dpi=150)
    if len(test_results) == 1:
        axes = [axes]
        
    for ax, (model_name, metrics) in zip(axes, test_results.items()):
        cm = np.array([
            [metrics["TP"], metrics["FN"]],
            [metrics["FP"], metrics["TN"]]
        ])
        cax = ax.matshow(cm, cmap="Blues", alpha=0.85)
        for i in range(2):
            for j in range(2):
                val = cm[i, j]
                label_txt = ["TP", "FN"][j] if i == 0 else ["FP", "TN"][j]
                ax.text(j, i, f"{label_txt}\n{val}", ha="center", va="center", fontsize=11, fontweight="bold")
                
        ax.set_title(model_name.replace(" - ", "\n"), fontsize=10, fontweight="bold", pad=10)
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(["Ngập (1)", "K.Ngập (0)"])
        ax.set_yticklabels(["Ngập (1)", "K.Ngập (0)"])
        ax.set_xlabel("Dự đoán", fontsize=10)
        ax.set_ylabel("Thực tế", fontsize=10)
        
    cm_grid_path = os.path.join(output_dir, "confusion_matrices_test.png")
    plt.tight_layout()
    plt.savefig(cm_grid_path)
    plt.close()
    logging.info(f"Đã lưu hình ma trận nhầm lẫn vào: {cm_grid_path}")
    return cm_grid_path
