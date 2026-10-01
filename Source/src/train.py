# -*- coding: utf-8 -*-
"""
IE403 - Khai thác Dữ liệu và Truyền thông Xã hội | UIT - ĐHQG-HCM
Đề tài: Hệ Thống Dự Báo Nguy Cơ Mưa Ngập Cục Bộ Khu Vực UIT & Thủ Đức Dựa Trên Quy Trình KDD
Bản quyền (C) 2026 Nguyễn Duy Nhiệm. Bảo lưu mọi quyền.
Tác giả: Nguyễn Duy Nhiệm (https://github.com/DuyNhiemUIT)
SPDX-License-Identifier: MIT
"""

"""
Module: train.py
Mục đích: Điều phối toàn bộ quy trình huấn luyện và đánh giá mô hình của Đồ án IE403:
1. Nạp dữ liệu Train, Validation, Test (đã được tiền xử lý & phân chia stratified).
2. Trích xuất Reducts bằng Lý thuyết tập thô (Rough Set).
3. Huấn luyện các mô hình:
   - ID3 (Information Gain) - Toàn bộ đặc trưng & Reduct
   - CART (Gini Index) - Toàn bộ đặc trưng & Reduct
   - Naive Bayes (Laplace) - Toàn bộ đặc trưng & Reduct
4. Lựa chọn mô hình tốt nhất (Champion Model) dựa trên F1-Score tập Validation.
5. Đánh giá kiểm định cuối cùng trên tập Test độc lập.
6. Lưu trữ mô hình vào thư mục `models/` và xuất biểu đồ so sánh.
"""

import os
import sys
import json
import pickle
import logging
import pandas as pd
import numpy as np

# Thêm thư mục hiện tại vào sys.path để import các module con
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from rough_set import RoughSetAnalyzer
from decision_tree import ID3DecisionTree, train_and_export_cart_tree
from naive_bayes import LaplaceNaiveBayes
from evaluation import evaluate_models_on_dataset, plot_model_comparison, plot_confusion_matrix_grid

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        
    base_dir = os.path.dirname(CURRENT_DIR)
    data_dir = os.path.join(base_dir, "data", "processed")
    models_dir = os.path.join(base_dir, "models")
    outputs_dir = os.path.join(base_dir, "outputs")
    
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)
    
    # 1. Nạp dữ liệu
    train_df = pd.read_csv(os.path.join(data_dir, "train_discrete.csv"))
    val_df = pd.read_csv(os.path.join(data_dir, "val_discrete.csv"))
    test_df = pd.read_csv(os.path.join(data_dir, "test_discrete.csv"))
    
    all_features = ["NhietDo", "DoAm", "ApSuat", "Gio", "HuongGio", "BienDoNhiet"]
    target_col = "Rain_Flood_Risk"
    
    logging.info(f"Đã nạp dữ liệu: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}.")
    
    # 2. Chạy Rough Set để tìm Reduct
    rough_analyzer = RoughSetAnalyzer(all_features, target_col)
    reducts = rough_analyzer.find_reducts_discernibility_matrix(train_df)
    greedy_reduct = rough_analyzer.find_greedy_reduct(train_df)
    
    # Chọn reduct đại diện
    best_reduct = greedy_reduct if len(greedy_reduct) < len(reducts[0]) else reducts[0]
    logging.info(f"Reduct đại diện được chọn: {best_reduct}")
    
    # Trích xuất luật 100%
    rules_100 = rough_analyzer.extract_100_percent_rules(train_df, best_reduct)
    
    # 3. Khởi tạo và huấn luyện danh sách mô hình
    models_to_evaluate = {}
    
    # Mô hình 1: ID3 - Full features
    logging.info("Huấn luyện ID3 (Full 6 Features)...")
    id3_full = ID3DecisionTree(max_depth=4, min_samples_split=10)
    id3_full.fit(train_df[all_features], train_df[target_col])
    models_to_evaluate["ID3 - Full Features"] = {
        "model": id3_full,
        "features": all_features
    }
    
    # Mô hình 2: ID3 - Reduct
    logging.info(f"Huấn luyện ID3 (Reduct: {best_reduct})...")
    id3_reduct = ID3DecisionTree(max_depth=4, min_samples_split=10)
    id3_reduct.fit(train_df[best_reduct], train_df[target_col])
    models_to_evaluate["ID3 - Reduct Features"] = {
        "model": id3_reduct,
        "features": best_reduct
    }
    
    # Mô hình 3: Naive Bayes (Laplace) - Full features
    logging.info("Huấn luyện Naive Bayes Laplace (Full 6 Features)...")
    nb_full = LaplaceNaiveBayes(use_laplace=True)
    nb_full.fit(train_df[all_features], train_df[target_col])
    models_to_evaluate["Naive Bayes - Full Features"] = {
        "model": nb_full,
        "features": all_features
    }
    
    # Mô hình 4: Naive Bayes (Laplace) - Reduct
    logging.info(f"Huấn luyện Naive Bayes Laplace (Reduct: {best_reduct})...")
    nb_reduct = LaplaceNaiveBayes(use_laplace=True)
    nb_reduct.fit(train_df[best_reduct], train_df[target_col])
    models_to_evaluate["Naive Bayes - Reduct Features"] = {
        "model": nb_reduct,
        "features": best_reduct
    }
    
    # Mô hình 5: CART (Gini Index) - Full features
    logging.info("Huấn luyện CART (Full 6 Features)...")
    cart_full, enc_cols_full = train_and_export_cart_tree(train_df, val_df, all_features, target_col, outputs_dir)
    models_to_evaluate["CART - Full Features"] = {
        "model": cart_full,
        "features": all_features,
        "encoded_cols": enc_cols_full
    }
    
    # Mô hình 6: CART (Gini Index) - Reduct
    logging.info(f"Huấn luyện CART (Reduct: {best_reduct})...")
    cart_reduct, enc_cols_reduct = train_and_export_cart_tree(train_df, val_df, best_reduct, target_col, outputs_dir)
    models_to_evaluate["CART - Reduct Features"] = {
        "model": cart_reduct,
        "features": best_reduct,
        "encoded_cols": enc_cols_reduct
    }
    
    # 4. Đánh giá trên tập Validation để chọn Champion Model
    logging.info("\n--- ĐÁNH GIÁ TRÊN TẬP VALIDATION (CHỌN MÔ HÌNH TỐT NHẤT) ---")
    val_results = evaluate_models_on_dataset(models_to_evaluate, val_df, val_df[target_col].values, "Validation")
    
    # Chọn mô hình có F1-Score cao nhất trên Validation
    best_model_name = max(val_results, key=lambda m: (val_results[m]["F1_Score"], val_results[m]["Recall"]))
    logging.info(f"CHAMPION MODEL ĐƯỢC CHỌN: {best_model_name} (F1 Val = {val_results[best_model_name]['F1_Score']:.4f})")
    
    # 5. Đánh giá kiểm định cuối cùng trên tập Test độc lập (Chỉ chạy 1 lần)
    logging.info("\n--- ĐÁNH GIÁ TRÊN TẬP TEST ĐỘC LẬP (KIỂM ĐỊNH KHÁCH QUAN) ---")
    test_results = evaluate_models_on_dataset(models_to_evaluate, test_df, test_df[target_col].values, "Test")
    
    # 6. Vẽ biểu đồ so sánh và ma trận nhầm lẫn
    plot_model_comparison(val_results, test_results, outputs_dir)
    plot_confusion_matrix_grid(test_results, outputs_dir)
    
    # 7. Lưu kết quả tổng hợp vào JSON & CSV
    summary_report = {
        "best_model_name": best_model_name,
        "reduct_selected": best_reduct,
        "validation_results": val_results,
        "test_results": test_results
    }
    summary_path = os.path.join(outputs_dir, "evaluation_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_report, f, indent=4, ensure_ascii=False)
        
    summary_df = pd.DataFrame([
        {
            "Mô Hình": m_name,
            "Val_Accuracy": val_results[m_name]["Accuracy"],
            "Val_Precision": val_results[m_name]["Precision"],
            "Val_Recall": val_results[m_name]["Recall"],
            "Val_F1": val_results[m_name]["F1_Score"],
            "Test_Accuracy": test_results[m_name]["Accuracy"],
            "Test_Precision": test_results[m_name]["Precision"],
            "Test_Recall": test_results[m_name]["Recall"],
            "Test_F1": test_results[m_name]["F1_Score"],
            "Test_TP": test_results[m_name]["TP"],
            "Test_FN": test_results[m_name]["FN"],
            "Test_FP": test_results[m_name]["FP"],
            "Test_TN": test_results[m_name]["TN"]
        }
        for m_name in models_to_evaluate
    ])
    summary_csv_path = os.path.join(outputs_dir, "evaluation_summary.csv")
    summary_df.to_csv(summary_csv_path, index=False, encoding="utf-8")
    
    # 8. Lưu các mô hình đã huấn luyện vào thư mục models/
    champion_info = models_to_evaluate[best_model_name]
    champion_path = os.path.join(models_dir, "champion_model.pkl")
    with open(champion_path, "wb") as f:
        pickle.dump({
            "model_name": best_model_name,
            "model": champion_info["model"],
            "features": champion_info["features"],
            "encoded_cols": champion_info.get("encoded_cols", None)
        }, f)
        
    # Lưu toàn bộ gói mô hình phục vụ Web App
    all_bundle_path = os.path.join(models_dir, "all_models_bundle.pkl")
    with open(all_bundle_path, "wb") as f:
        pickle.dump(models_to_evaluate, f)
        
    logging.info(f"Đã lưu mô hình Champion vào: {champion_path}")
    logging.info(f"Đã lưu bảng tổng kết hiệu suất vào: {summary_csv_path}")
    
    print("\n" + "="*80)
    print("BẢNG TỔNG HỢP HIỆU SUẤT TRÊN TẬP TEST ĐỘC LẬP (IE403 - ĐÁNH GIÁ MÔ HÌNH)")
    print("="*80)
    print(summary_df[["Mô Hình", "Test_Accuracy", "Test_Precision", "Test_Recall", "Test_F1"]].to_string(index=False))
    print("="*80)
    print(f"MÔ HÌNH VÔ ĐỊCH (CHAMPION MODEL): {best_model_name}")
    print(f"F1 Test: {test_results[best_model_name]['F1_Score']:.4f} | Recall Test: {test_results[best_model_name]['Recall']:.4f}")
    print("="*80)

if __name__ == "__main__":
    main()
