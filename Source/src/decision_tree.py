# -*- coding: utf-8 -*-
"""
IE403 - Khai thác Dữ liệu và Truyền thông Xã hội | UIT - ĐHQG-HCM
Đề tài: Hệ Thống Dự Báo Nguy Cơ Mưa Ngập Cục Bộ Khu Vực UIT & Thủ Đức Dựa Trên Quy Trình KDD
Bản quyền (C) 2026 Nguyễn Duy Nhiệm. Bảo lưu mọi quyền.
Tác giả: Nguyễn Duy Nhiệm (https://github.com/DuyNhiemUIT)
SPDX-License-Identifier: MIT
"""

"""
Module: decision_tree.py
Mục đích: Cài đặt thuật toán phân lớp Cây quyết định (Decision Tree)
theo đúng bài giảng Bài 5 (Thầy Mai Xuân Hùng - UIT):
1. Thuật toán ID3: Sử dụng Entropy và Độ lợi thông tin (Information Gain).
2. Thuật toán CART: Sử dụng Chỉ số Gini (Gini Index).
3. Trích xuất luật phân lớp dạng IF-THEN từ các đường dẫn từ gốc đến lá.
4. Trực quan hóa cây quyết định và lưu đồ họa ra file PNG.
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class ID3DecisionTree:
    """
    Thuật toán ID3 thuần túy trên các biến định tính/rời rạc theo giáo trình:
    I(s1, ..., sm) = - sum (pi * log2(pi))
    E(A) = sum (|Sj|/|S| * I(Sj))
    Gain(A) = I(S) - E(A)
    """
    def __init__(self, max_depth=5, min_samples_split=5):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.tree = None
        self.classes = []

    def _entropy(self, y):
        counts = np.bincount(y)
        probs = counts[counts > 0] / len(y)
        return -np.sum(probs * np.log2(probs))

    def _information_gain(self, X_col, y):
        total_entropy = self._entropy(y)
        n = len(y)
        unique_vals = np.unique(X_col)
        weighted_entropy = 0.0
        
        for val in unique_vals:
            sub_y = y[X_col == val]
            if len(sub_y) > 0:
                weighted_entropy += (len(sub_y) / n) * self._entropy(sub_y)
                
        return total_entropy - weighted_entropy

    def fit(self, X, y):
        self.classes = list(np.unique(y))
        feature_names = list(X.columns)
        self.tree = self._build_tree(X.values, y.values, feature_names, depth=0)
        return self

    def _build_tree(self, X, y, feature_names, depth):
        n_samples, n_features = X.shape
        unique_classes, counts = np.unique(y, return_counts=True)
        majority_class = unique_classes[np.argmax(counts)]

        # Điều kiện dừng
        if len(unique_classes) == 1:
            return {"type": "leaf", "class": int(unique_classes[0]), "samples": n_samples, "prob": 1.0}
            
        if depth >= self.max_depth or n_samples < self.min_samples_split or n_features == 0:
            prob = np.max(counts) / n_samples
            return {"type": "leaf", "class": int(majority_class), "samples": n_samples, "prob": round(float(prob), 4)}

        # Tính Information Gain cho từng thuộc tính
        gains = [self._information_gain(X[:, i], y) for i in range(n_features)]
        best_feat_idx = int(np.argmax(gains))
        best_gain = gains[best_feat_idx]

        if best_gain <= 1e-6:
            prob = np.max(counts) / n_samples
            return {"type": "leaf", "class": int(majority_class), "samples": n_samples, "prob": round(float(prob), 4)}

        best_feat_name = feature_names[best_feat_idx]
        node = {
            "type": "node",
            "feature": best_feat_name,
            "gain": round(float(best_gain), 4),
            "samples": n_samples,
            "majority_class": int(majority_class),
            "children": {}
        }

        # Tách nhánh theo từng giá trị của thuộc tính
        unique_vals = np.unique(X[:, best_feat_idx])
        sub_feature_names = [f for i, f in enumerate(feature_names) if i != best_feat_idx]

        for val in unique_vals:
            mask = (X[:, best_feat_idx] == val)
            sub_X = np.delete(X[mask], best_feat_idx, axis=1)
            sub_y = y[mask]
            node["children"][str(val)] = self._build_tree(sub_X, sub_y, sub_feature_names, depth + 1)

        return node

    def predict_one(self, sample, node=None):
        if node is None:
            node = self.tree
        if node["type"] == "leaf":
            return node["class"]

        feat = node["feature"]
        val = str(sample.get(feat, ""))
        if val in node["children"]:
            return self.predict_one(sample, node["children"][val])
        else:
            return node["majority_class"]

    def predict(self, X_df):
        return np.array([self.predict_one(row) for _, row in X_df.iterrows()])

    def extract_rules(self, node=None, current_path=None):
        """
        Trích xuất luật phân lớp IF-THEN từ cây ID3 (slide Bài 5, slide 64)
        """
        if node is None:
            node = self.tree
        if current_path is None:
            current_path = []

        if node["type"] == "leaf":
            rule_str = " AND ".join(current_path) if current_path else "ALWAYS"
            return [{
                "rule": f"IF {rule_str} THEN (Rain_Flood_Risk = {node['class']})",
                "class": node["class"],
                "samples": node["samples"],
                "confidence": node["prob"]
            }]

        rules = []
        feat = node["feature"]
        for val, child in node["children"].items():
            new_path = current_path + [f"({feat} = '{val}')"]
            rules.extend(self.extract_rules(child, new_path))
        return rules

def train_and_export_cart_tree(train_df, val_df, feature_cols, target_col, output_dir):
    """
    Huấn luyện mô hình CART (Gini Index) sử dụng scikit-learn để so sánh với ID3
    và xuất hình ảnh cây quyết định trực quan chất lượng cao.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # One-hot encoding cho các biến phân loại
    X_train_raw = train_df[feature_cols]
    y_train = train_df[target_col].values
    X_val_raw = val_df[feature_cols]
    y_val = val_df[target_col].values
    
    X_train = pd.get_dummies(X_train_raw, drop_first=False)
    encoded_cols = list(X_train.columns)
    X_val = pd.get_dummies(X_val_raw, drop_first=False).reindex(columns=encoded_cols, fill_value=0)
    
    clf = DecisionTreeClassifier(criterion="gini", max_depth=4, min_samples_split=10, random_state=42)
    clf.fit(X_train, y_train)
    
    # Xuất hình ảnh cây
    plt.figure(figsize=(18, 9), dpi=150)
    plot_tree(
        clf,
        feature_names=encoded_cols,
        class_names=["An Toàn (0)", "Nguy Cơ Ngập (1)"],
        filled=True,
        rounded=True,
        fontsize=9
    )
    plt.title("Cây Quyết Định Dự Báo Nguy Cơ Mưa Ngập TP.HCM (Thuật Toán CART - Chỉ Số Gini)", fontsize=14, fontweight="bold", pad=15)
    tree_img_path = os.path.join(output_dir, "cart_decision_tree.png")
    plt.tight_layout()
    plt.savefig(tree_img_path)
    plt.close()
    logging.info(f"Đã xuất hình ảnh Cây quyết định CART vào: {tree_img_path}")
    
    text_rules = export_text(clf, feature_names=encoded_cols)
    rules_text_path = os.path.join(output_dir, "cart_decision_tree_rules.txt")
    with open(rules_text_path, "w", encoding="utf-8") as f:
        f.write(text_rules)
        
    return clf, encoded_cols

def run_decision_tree_pipeline(train_csv_path, val_csv_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    train_df = pd.read_csv(train_csv_path)
    val_df = pd.read_csv(val_csv_path)
    
    feature_cols = ["NhietDo", "DoAm", "ApSuat", "Gio", "HuongGio", "BienDoNhiet"]
    target_col = "Rain_Flood_Risk"
    
    # 1. Huấn luyện ID3
    logging.info("Huấn luyện mô hình ID3 (Information Gain)...")
    id3 = ID3DecisionTree(max_depth=4, min_samples_split=10)
    id3.fit(train_df[feature_cols], train_df[target_col])
    id3_rules = id3.extract_rules()
    
    # Lưu luật ID3
    rules_df = pd.DataFrame(id3_rules)
    id3_rules_path = os.path.join(output_dir, "id3_decision_tree_rules.csv")
    rules_df.to_csv(id3_rules_path, index=False, encoding="utf-8")
    logging.info(f"Đã lưu {len(id3_rules)} luật ID3 vào: {id3_rules_path}")
    
    # Lưu cấu trúc cây ID3 JSON
    id3_json_path = os.path.join(output_dir, "id3_tree_structure.json")
    with open(id3_json_path, "w", encoding="utf-8") as f:
        json.dump(id3.tree, f, indent=4, ensure_ascii=False)
        
    # 2. Huấn luyện CART
    logging.info("Huấn luyện mô hình CART (Gini Index)...")
    cart_model, encoded_cols = train_and_export_cart_tree(train_df, val_df, feature_cols, target_col, output_dir)
    
    return {
        "id3_rules_count": len(id3_rules),
        "sample_id3_rules": id3_rules[:5],
        "cart_tree_depth": cart_model.get_depth(),
        "cart_n_leaves": cart_model.get_n_leaves(),
        "encoded_cols": encoded_cols
    }

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    base_dir = os.path.dirname(os.path.dirname(__file__))
    train_path = os.path.join(base_dir, "data", "processed", "train_discrete.csv")
    val_path = os.path.join(base_dir, "data", "processed", "val_discrete.csv")
    out_dir = os.path.join(base_dir, "outputs")
    res = run_decision_tree_pipeline(train_path, val_path, out_dir)
    print("\n=== KET QUA HUAN LUYEN CAY QUYET DINH ===")
    print(f"So luong luat trich xuat tu ID3: {res['id3_rules_count']}")
    print("Mau 2 luat ID3:")
    for r in res["sample_id3_rules"][:2]:
        print(f"  * {r['rule']} (Samples={r['samples']}, Conf={r['confidence']})")
    print(f"CART Do sau cay: {res['cart_tree_depth']}, So nut la: {res['cart_n_leaves']}")

if __name__ == "__main__":
    main()
