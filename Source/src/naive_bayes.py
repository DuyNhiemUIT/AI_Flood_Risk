# -*- coding: utf-8 -*-
"""
IE403 - Khai thác Dữ liệu và Truyền thông Xã hội | UIT - ĐHQG-HCM
Đề tài: Hệ Thống Dự Báo Nguy Cơ Mưa Ngập Cục Bộ Khu Vực UIT & Thủ Đức Dựa Trên Quy Trình KDD
Bản quyền (C) 2026 Nguyễn Duy Nhiệm. Bảo lưu mọi quyền.
Tác giả: Nguyễn Duy Nhiệm (https://github.com/DuyNhiemUIT)
SPDX-License-Identifier: MIT
"""

"""
Module: naive_bayes.py
Mục đích: Cài đặt thuật toán phân lớp Naive Bayes kèm kỹ thuật làm trơn Laplace
theo đúng bài giảng Bài 5.1 & Bài 7 (Thầy Mai Xuân Hùng - UIT):
P(Ci) = (|Ci,D| + 1) / (|D| + m)
P(xk | Ci) = (#Ci,D{xk} + 1) / (|Ci,D| + r_k)
Trong đó:
- m: Số phân lớp (m = 2)
- r_k: Số giá trị phân biệt của thuộc tính thứ k
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class LaplaceNaiveBayes:
    """
    Mô hình phân lớp Naive Bayes rời rạc tích hợp kỹ thuật làm trơn Laplace chuẩn mực.
    """
    def __init__(self, use_laplace=True):
        self.use_laplace = use_laplace
        self.class_priors = {}
        self.feature_likelihoods = {}
        self.classes = []
        self.feature_cardinalities = {}
        self.feature_domains = {}
        self.m_classes = 0

    def fit(self, X_df, y_series):
        self.classes = sorted(list(y_series.unique()))
        self.m_classes = len(self.classes)
        total_samples = len(y_series)
        
        # 1. Lưu miền giá trị và lực lượng miền giá trị (r_k) của từng thuộc tính
        for col in X_df.columns:
            domain = sorted(list(X_df[col].unique()))
            self.feature_domains[col] = domain
            self.feature_cardinalities[col] = len(domain)
            
        # 2. Tính xác suất tiên nghiệm P(C_i) (Prior probability)
        for c in self.classes:
            count_c = (y_series == c).sum()
            if self.use_laplace:
                # P(Ci) = (|Ci,D| + 1) / (|D| + m)
                self.class_priors[c] = (count_c + 1.0) / (total_samples + self.m_classes)
            else:
                self.class_priors[c] = count_c / total_samples

        # 3. Tính xác suất có điều kiện P(x_k | C_i) (Conditional Likelihood)
        self.feature_likelihoods = {c: {} for c in self.classes}
        for c in self.classes:
            sub_X = X_df[y_series == c]
            count_c = len(sub_X)
            
            for col in X_df.columns:
                self.feature_likelihoods[c][col] = {}
                r_k = self.feature_cardinalities[col]
                
                val_counts = sub_X[col].value_counts().to_dict()
                for val in self.feature_domains[col]:
                    count_val_c = val_counts.get(val, 0)
                    if self.use_laplace:
                        # P(xk | Ci) = (#Ci,D{xk} + 1) / (|Ci,D| + r_k)
                        prob = (count_val_c + 1.0) / (count_c + r_k)
                    else:
                        prob = count_val_c / count_c if count_c > 0 else 0.0
                    self.feature_likelihoods[c][col][val] = prob

        logging.info(f"Đã huấn luyện Naive Bayes (Laplace={self.use_laplace}): {len(self.classes)} lớp, {len(X_df.columns)} thuộc tính.")
        return self

    def predict_proba_one(self, sample_dict):
        """
        Tính xác suất hậu nghiệm P(C_i | X) theo Định lý Bayes:
        P(C_i | X) proportional to P(C_i) * prod_{k} P(x_k | C_i)
        """
        posterior = {}
        for c in self.classes:
            p = self.class_priors[c]
            for col, val in sample_dict.items():
                if col in self.feature_likelihoods[c]:
                    # Nếu gặp giá trị mới chưa có trong tập train, Laplace smoothing gán 1 / (|Ci,D| + r_k)
                    if val in self.feature_likelihoods[c][col]:
                        prob_feat = self.feature_likelihoods[c][col][val]
                    else:
                        # Làm trơn cho giá trị chưa từng thấy
                        r_k = self.feature_cardinalities[col] + 1
                        prob_feat = 1.0 / (r_k * 10.0) if self.use_laplace else 0.0
                    p *= prob_feat
            posterior[c] = p
            
        # Chuẩn hóa về tổng = 1.0
        total_p = sum(posterior.values())
        if total_p > 0:
            return {c: round(posterior[c] / total_p, 4) for c in self.classes}
        else:
            return {c: 1.0 / self.m_classes for c in self.classes}

    def predict_one(self, sample_dict):
        proba = self.predict_proba_one(sample_dict)
        return max(proba, key=proba.get)

    def predict(self, X_df):
        return np.array([self.predict_one(row.to_dict()) for _, row in X_df.iterrows()])

    def predict_proba(self, X_df):
        return np.array([[p[c] for c in self.classes] for p in [self.predict_proba_one(row.to_dict()) for _, row in X_df.iterrows()]])

def run_naive_bayes_pipeline(train_csv_path, val_csv_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    train_df = pd.read_csv(train_csv_path)
    val_df = pd.read_csv(val_csv_path)
    
    feature_cols = ["NhietDo", "DoAm", "ApSuat", "Gio", "HuongGio", "BienDoNhiet"]
    target_col = "Rain_Flood_Risk"
    
    # 1. Huấn luyện Naive Bayes có làm trơn Laplace
    nb_laplace = LaplaceNaiveBayes(use_laplace=True)
    nb_laplace.fit(train_df[feature_cols], train_df[target_col])
    
    # 2. Huấn luyện Naive Bayes KHÔNG làm trơn để so sánh
    nb_standard = LaplaceNaiveBayes(use_laplace=False)
    nb_standard.fit(train_df[feature_cols], train_df[target_col])
    
    # Đánh giá trên tập Validation
    preds_laplace = nb_laplace.predict(val_df[feature_cols])
    preds_standard = nb_standard.predict(val_df[feature_cols])
    y_val = val_df[target_col].values
    
    acc_laplace = np.mean(preds_laplace == y_val)
    acc_standard = np.mean(preds_standard == y_val)
    
    # Lưu bảng xác suất có điều kiện P(xk | Ci)
    prob_tables = {
        "class_priors": {str(k): round(v, 4) for k, v in nb_laplace.class_priors.items()},
        "likelihoods": {
            str(c): {
                col: {str(val): round(prob, 4) for val, prob in nb_laplace.feature_likelihoods[c][col].items()}
                for col in feature_cols
            }
            for c in nb_laplace.classes
        }
    }
    prob_table_path = os.path.join(output_dir, "naive_bayes_laplace_tables.json")
    with open(prob_table_path, "w", encoding="utf-8") as f:
        json.dump(prob_tables, f, indent=4, ensure_ascii=False)
        
    logging.info(f"Đã lưu bảng xác suất Naive Bayes vào: {prob_table_path}")
    return {
        "accuracy_laplace": round(float(acc_laplace), 4),
        "accuracy_standard": round(float(acc_standard), 4),
        "priors": prob_tables["class_priors"]
    }

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    base_dir = os.path.dirname(os.path.dirname(__file__))
    train_path = os.path.join(base_dir, "data", "processed", "train_discrete.csv")
    val_path = os.path.join(base_dir, "data", "processed", "val_discrete.csv")
    out_dir = os.path.join(base_dir, "outputs")
    res = run_naive_bayes_pipeline(train_path, val_path, out_dir)
    print("\n=== KET QUA HUAN LUYEN NAIVE BAYES (LAPLACE SMOOTHING) ===")
    print(f"Xac suat tien nghiem P(Ci): {res['priors']}")
    print(f"Do chinh xac tren Validation (Co Laplace): {res['accuracy_laplace'] * 100:.2f}%")
    print(f"Do chinh xac tren Validation (Khong Laplace): {res['accuracy_standard'] * 100:.2f}%")

if __name__ == "__main__":
    main()
