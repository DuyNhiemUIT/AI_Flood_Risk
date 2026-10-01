# -*- coding: utf-8 -*-
"""
IE403 - Khai thác Dữ liệu và Truyền thông Xã hội | UIT - ĐHQG-HCM
Đề tài: Hệ Thống Dự Báo Nguy Cơ Mưa Ngập Cục Bộ Khu Vực UIT & Thủ Đức Dựa Trên Quy Trình KDD
Bản quyền (C) 2026 Nguyễn Duy Nhiệm. Bảo lưu mọi quyền.
Tác giả: Nguyễn Duy Nhiệm (https://github.com/DuyNhiemUIT)
SPDX-License-Identifier: MIT
"""

"""
Module: rough_set.py
Mục đích: Cài đặt lý thuyết Tập thô (Rough Set Theory - Zdzisław Pawlak 1982)
và thuật toán trích chọn đặc trưng Reduct theo đúng bài giảng Bài 3 (Thầy Mai Xuân Hùng - UIT):
1. Hệ quyết định DS = (U, C U {d}).
2. Quan hệ bất khả phân biệt IND(B) và các lớp tương đương U/IND(B).
3. Xấp xỉ dưới, xấp xỉ trên, vùng biên và độ chính xác xấp xỉ alpha_B(X).
4. Độ phụ thuộc thuộc tính gamma(C, d) = k.
5. Ma trận phân biệt (Discernibility Matrix) và hàm phân biệt Boole.
6. Trích xuất Reducts (Rút gọn thuộc tính) tối thiểu.
7. Sinh tập luật quyết định có độ chính xác phân lớp 100%.
"""

import os
import sys
import json
import logging
from itertools import combinations
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class RoughSetAnalyzer:
    def __init__(self, condition_attrs, decision_attr):
        self.condition_attrs = list(condition_attrs)
        self.decision_attr = decision_attr
        self.reducts = []
        self.best_reduct = []
        self.rules_100 = []
        
    def get_indiscernibility_classes(self, df, attributes):
        """
        Tính các lớp tương đương U/IND(B) của các đối tượng không thể phân biệt theo tập thuộc tính B.
        Trả về dictionary: { (val1, val2, ...): [danh sách index đối tượng] }
        """
        classes = {}
        for idx, row in df.iterrows():
            key = tuple(row[attr] for attr in attributes)
            if key not in classes:
                classes[key] = []
            classes[key].append(idx)
        return classes

    def compute_approximations(self, df, attributes, decision_classes=None):
        """
        Tính Xấp xỉ dưới, Xấp xỉ trên, Vùng biên và Độ chính xác xấp xỉ alpha:
        - Lower Approximation (B_lower): Các lớp tương đương nằm hoàn toàn trong X
        - Upper Approximation (B_upper): Các lớp tương đương có giao khác rỗng với X
        - Boundary (B_boundary) = B_upper - B_lower
        - Accuracy: alpha = |B_lower| / |B_upper|
        (Đúng theo slide Bài 3, slide 14-18)
        """
        if decision_classes is None:
            # Phân hoạch U/d
            decision_classes = {}
            for d_val in df[self.decision_attr].unique():
                decision_classes[d_val] = set(df[df[self.decision_attr] == d_val].index)
                
        ind_classes = self.get_indiscernibility_classes(df, attributes)
        
        results = {}
        for d_val, x_set in decision_classes.items():
            lower = set()
            upper = set()
            
            for eq_key, eq_indices in ind_classes.items():
                eq_set = set(eq_indices)
                if eq_set.issubset(x_set):
                    lower.update(eq_set)
                if not eq_set.isdisjoint(x_set):
                    upper.update(eq_set)
                    
            boundary = upper - lower
            alpha = len(lower) / len(upper) if len(upper) > 0 else 1.0
            
            results[int(d_val)] = {
                "lower_size": int(len(lower)),
                "upper_size": int(len(upper)),
                "boundary_size": int(len(boundary)),
                "accuracy_alpha": round(alpha, 4),
                "is_rough": bool(len(boundary) > 0),
                "lower_indices": [int(x) for x in list(lower)[:50]],
                "upper_indices": [int(x) for x in list(upper)[:50]]
            }
        return results

    def compute_dependency_degree(self, df, attributes):
        """
        Tính độ phụ thuộc thuộc tính gamma(B, d) = k:
        k = (sum_{X in U/d} |B_lower(X)|) / |U|
        (Đúng theo slide Bài 3, slide 29)
        k = 1: d phụ thuộc hoàn toàn vào B.
        k < 1: d phụ thuộc một phần (theo mức độ k) vào B.
        """
        total_u = len(df)
        if total_u == 0 or len(attributes) == 0:
            return 0.0
            
        approximations = self.compute_approximations(df, attributes)
        sum_lower = sum(res["lower_size"] for res in approximations.values())
        k = sum_lower / total_u
        return round(float(k), 4)

    def find_reducts_discernibility_matrix(self, df):
        """
        Xác định Ma trận phân biệt và Hàm phân biệt Boole để tìm tập Reducts tối thiểu
        (Đúng theo slide Bài 3, slide 22-28):
        - Gom cụm các dòng giống nhau thành các bộ giá trị đại diện (để tối ưu hóa tốc độ).
        - c_ij = { a in C | a(x_i) != a(x_j) } với các cặp có nhãn quyết định khác nhau d(x_i) != d(x_j).
        - Rút gọn hàm phân biệt Boole bằng luật hấp thu: A and (A or B) = A.
        """
        logging.info("Đang xây dựng Ma trận phân biệt (Discernibility Matrix)...")
        # Nhóm các đối tượng có cùng vector thuộc tính điều kiện và nhãn
        grouped = df.groupby(self.condition_attrs + [self.decision_attr]).size().reset_index(name="_count")
        n_unique = len(grouped)
        logging.info(f"Rút gọn {len(df)} đối tượng thành {n_unique} nhóm trạng thái duy nhất.")
        
        clauses = set()
        for i in range(n_unique):
            d_i = grouped.loc[i, self.decision_attr]
            for j in range(i + 1, n_unique):
                d_j = grouped.loc[j, self.decision_attr]
                if d_i != d_j:
                    diff_attrs = []
                    for attr in self.condition_attrs:
                        if grouped.loc[i, attr] != grouped.loc[j, attr]:
                            diff_attrs.append(attr)
                    if diff_attrs:
                        # Tuyển Boole: a or b or c...
                        clauses.add(frozenset(diff_attrs))
                        
        logging.info(f"Ma trận phân biệt sinh ra {len(clauses)} mệnh đề tuyển Boole khác rỗng.")
        
        # Rút gọn Boole bằng Luật Hấp thu: nếu c1 là tập con của c2 thì c1 and c2 = c1 (bỏ c2)
        simplified_clauses = []
        sorted_clauses = sorted(list(clauses), key=lambda s: len(s))
        for c in sorted_clauses:
            is_absorbed = False
            for kept in simplified_clauses:
                if kept.issubset(c):
                    is_absorbed = True
                    break
            if not is_absorbed:
                simplified_clauses.append(c)
                
        logging.info(f"Sau khi áp dụng Luật hấp thu Boole, còn {len(simplified_clauses)} mệnh đề cốt lõi.")
        
        # Tìm các Reducts tối thiểu bằng cách duyệt tổ hợp từ kích thước nhỏ đến lớn
        minimal_reducts = []
        for k in range(1, len(self.condition_attrs) + 1):
            for candidate in combinations(self.condition_attrs, k):
                cand_set = set(candidate)
                # candidate là hitting set nếu nó giao khác rỗng với TẤT CẢ các mệnh đề
                if all(bool(cand_set.intersection(cl)) for cl in simplified_clauses):
                    # Kiểm tra tính tối thiểu: không chứa reduct con nào đã tìm thấy
                    if not any(set(r).issubset(cand_set) for r in minimal_reducts):
                        minimal_reducts.append(list(candidate))
            if minimal_reducts:
                # Dừng ở kích thước nhỏ nhất để lấy reducts tối thiểu
                break
                
        # Nếu chưa tìm thấy (do mâu thuẫn dữ liệu), dùng Greedy Reduct theo độ phụ thuộc k
        if not minimal_reducts:
            minimal_reducts = [self.find_greedy_reduct(df)]
            
        self.reducts = minimal_reducts
        self.best_reduct = minimal_reducts[0]
        logging.info(f"Đã tìm thấy {len(minimal_reducts)} Reduct tối thiểu: {minimal_reducts}")
        return minimal_reducts

    def find_greedy_reduct(self, df):
        """
        Giải thuật tham lam (Greedy Heuristic Reduct) dựa trên gia số độ phụ thuộc gamma(B, d):
        Tại mỗi bước, chọn thuộc tính a mang lại gamma(B U {a}, d) cao nhất cho đến khi đạt gamma tối đa.
        """
        selected = []
        current_k = 0.0
        max_possible_k = self.compute_dependency_degree(df, self.condition_attrs)
        remaining = list(self.condition_attrs)
        
        while remaining and current_k < max_possible_k:
            best_attr = None
            best_k = current_k
            for attr in remaining:
                cand = selected + [attr]
                k_cand = self.compute_dependency_degree(df, cand)
                if k_cand > best_k:
                    best_k = k_cand
                    best_attr = attr
            if best_attr is not None:
                selected.append(best_attr)
                remaining.remove(best_attr)
                current_k = best_k
            else:
                break
        return selected if selected else self.condition_attrs

    def extract_100_percent_rules(self, df, reduct=None):
        """
        Trích xuất các luật quyết định có độ chính xác phân lớp 100%:
        (Đúng theo slide Bài 3, slide 39-43)
        Nếu một lớp tương đương Z của Reduct là tập con của X_j (Z subseteq X_j)
        thì ta rút ra được luật chắc chắn đúng 100%:
        R: IF attr_1 = val_1 AND attr_2 = val_2 ... THEN Decision = d_val
        """
        if reduct is None:
            reduct = self.best_reduct if self.best_reduct else self.condition_attrs
            
        ind_classes = self.get_indiscernibility_classes(df, reduct)
        rules = []
        
        for eq_key, eq_indices in ind_classes.items():
            sub_df = df.loc[eq_indices]
            dec_counts = sub_df[self.decision_attr].value_counts()
            
            # Nếu 100% đối tượng trong lớp tương đương đều có cùng một nhãn quyết định
            if len(dec_counts) == 1:
                dec_val = dec_counts.index[0]
                rule_antecedent = {attr: val for attr, val in zip(reduct, eq_key)}
                support_count = len(eq_indices)
                rule_str = " AND ".join([f"({k} = '{v}')" for k, v in rule_antecedent.items()])
                rule_str = f"IF {rule_str} THEN ({self.decision_attr} = {dec_val})"
                
                rules.append({
                    "rule": rule_str,
                    "antecedent": rule_antecedent,
                    "consequent": int(dec_val),
                    "support": support_count,
                    "confidence": 1.0,
                    "accuracy": 1.0
                })
                
        # Sắp xếp theo độ hỗ trợ (số mẫu thỏa mãn) giảm dần
        rules.sort(key=lambda r: r["support"], reverse=True)
        self.rules_100 = rules
        logging.info(f"Đã trích xuất {len(rules)} luật quyết định có độ chính xác 100% từ Reduct {reduct}!")
        return rules

def run_rough_set_pipeline(train_csv_path, output_dir):
    """
    Thực thi trọn vẹn quy trình Tập thô trên tập dữ liệu Train:
    - Tính ma trận phân biệt và rút gọn Reduct
    - Tính độ phụ thuộc thuộc tính k
    - Trích xuất tập luật 100%
    - Lưu kết quả phân tích vào file JSON và CSV
    """
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(train_csv_path)
    
    condition_attrs = ["NhietDo", "DoAm", "ApSuat", "Gio", "HuongGio", "BienDoNhiet"]
    decision_attr = "Rain_Flood_Risk"
    
    analyzer = RoughSetAnalyzer(condition_attrs, decision_attr)
    
    # 1. Tính độ phụ thuộc toàn bộ thuộc tính ban đầu
    full_k = analyzer.compute_dependency_degree(df, condition_attrs)
    full_approx = analyzer.compute_approximations(df, condition_attrs)
    
    # 2. Tìm các Reduct tối thiểu
    reducts = analyzer.find_reducts_discernibility_matrix(df)
    greedy_reduct = analyzer.find_greedy_reduct(df)
    best_reduct = greedy_reduct if len(greedy_reduct) < len(reducts[0]) else reducts[0]
    analyzer.best_reduct = best_reduct
    
    # 3. Tính độ phụ thuộc trên Reduct tốt nhất
    reduct_k = analyzer.compute_dependency_degree(df, best_reduct)
    reduct_approx = analyzer.compute_approximations(df, best_reduct)
    
    # 4. Trích xuất luật 100%
    rules_100 = analyzer.extract_100_percent_rules(df, best_reduct)
    
    report = {
        "condition_attributes": condition_attrs,
        "decision_attribute": decision_attr,
        "full_attributes_dependency_k": full_k,
        "full_attributes_approximations": full_approx,
        "discovered_reducts": reducts,
        "greedy_reduct": greedy_reduct,
        "best_reduct": best_reduct,
        "reduct_dependency_k": reduct_k,
        "reduct_approximations": reduct_approx,
        "total_100_percent_rules": len(rules_100),
        "sample_top_rules": rules_100[:10]
    }
    
    report_path = os.path.join(output_dir, "rough_set_reduct_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
        
    rules_df = pd.DataFrame([
        {
            "Rule_ID": f"R{i+1}",
            "Rule": r["rule"],
            "Support_Count": r["support"],
            "Confidence": r["confidence"],
            "Consequent": r["consequent"]
        }
        for i, r in enumerate(rules_100)
    ])
    rules_path = os.path.join(output_dir, "rough_set_rules_100.csv")
    rules_df.to_csv(rules_path, index=False, encoding="utf-8")
    
    logging.info(f"Đã lưu báo cáo Rough Set vào: {report_path}")
    logging.info(f"Đã lưu danh sách luật 100% vào: {rules_path}")
    return report

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    base_dir = os.path.dirname(os.path.dirname(__file__))
    train_path = os.path.join(base_dir, "data", "processed", "train_discrete.csv")
    out_dir = os.path.join(base_dir, "outputs")
    report = run_rough_set_pipeline(train_path, out_dir)
    print("\n=== KET QUA PHAN TICH TAP THO (ROUGH SET & REDUCT) ===")
    print(f"Do phu thuoc k (Toan bo 6 thuoc tinh): {report['full_attributes_dependency_k']}")
    print(f"Cac Reducts tim duoc: {report['discovered_reducts']}")
    print(f"Reduct toi uu: {report['best_reduct']}")
    print(f"Do phu thuoc k tren Reduct: {report['reduct_dependency_k']}")
    print(f"Tong so luat chinh xac 100%: {report['total_100_percent_rules']}")
    print("Mau 3 luat dau tien:")
    for r in report["sample_top_rules"][:3]:
        print(f"  * {r['rule']} (Support={r['support']})")

if __name__ == "__main__":
    main()
