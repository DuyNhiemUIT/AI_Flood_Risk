# -*- coding: utf-8 -*-
"""
IE403 - Khai thác Dữ liệu và Truyền thông Xã hội | UIT - ĐHQG-HCM
Đề tài: Hệ Thống Dự Báo Nguy Cơ Mưa Ngập Cục Bộ Khu Vực UIT & Thủ Đức Dựa Trên Quy Trình KDD
Bản quyền (C) 2026 Nguyễn Duy Nhiệm. Bảo lưu mọi quyền.
Tác giả: Nguyễn Duy Nhiệm (https://github.com/DuyNhiemUIT)
SPDX-License-Identifier: MIT
"""

"""
Module: clustering.py
Mục đích: Cài đặt các thuật toán Gom cụm (Clustering) theo đúng bài giảng của Thầy Mai Xuân Hùng:
1. Thuật toán K-Means (Bài 6): Khởi tạo ma trận phân hoạch U, tính khoảng cách Minkowski/Euclid,
   cập nhật vector trọng tâm, lặp cho đến khi hội tụ (|U_n - U_{n-1}| < epsilon).
2. Thuật toán Mạng nơ-ron tự tổ chức Kohonen SOM (Bài 8): Tạo bản đồ 2 chiều, tìm nơ-ron chiến thắng BMU,
   cập nhật trọng số vùng lân cận N_c(t) với hệ số học alpha(t) suy giảm.
3. Phân cụm các hình thái thời tiết TP.HCM và trực quan hóa bản đồ cụm.
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class CustomKMeans:
    """
    Cài đặt thuật toán K-Means thuần túy theo từng bước trong slide Bài 6:
    - Bước 1: Khởi tạo k điểm trọng tâm ban đầu.
    - Bước 2: Khởi tạo ma trận phân hoạch U = (m_ij).
    - Bước 3: Tính vector trọng tâm v_i = sum(m_ij * x_j) / sum(m_ij).
    - Bước 4: Gán lại từng điểm vào cụm có trọng tâm gần nhất (Euclid).
    - Bước 5: Lặp cho đến khi |U_n - U_{n-1}| < epsilon thì dừng.
    """
    def __init__(self, k=3, max_iter=100, tol=1e-4, random_state=42):
        self.k = k
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.centroids = None
        self.labels_ = None
        self.inertia_ = 0.0

    def fit(self, X):
        np.random.seed(self.random_state)
        n_samples, n_features = X.shape
        
        # Chọn ngẫu nhiên k điểm làm tâm ban đầu
        rand_indices = np.random.choice(n_samples, self.k, replace=False)
        self.centroids = X[rand_indices].copy()
        
        # Khởi tạo ma trận phân hoạch U
        U_prev = np.zeros((self.k, n_samples))
        
        for iteration in range(self.max_iter):
            # Tính khoảng cách Euclid từ từng điểm đến tất cả các tâm cụm
            # d(x, v) = sqrt(sum((x - v)^2))
            distances = np.zeros((n_samples, self.k))
            for c_idx in range(self.k):
                distances[:, c_idx] = np.linalg.norm(X - self.centroids[c_idx], axis=1)
                
            labels = np.argmin(distances, axis=1)
            
            # Xây dựng ma trận phân hoạch U mới: m_ij = 1 nếu điểm j thuộc cụm i, ngược lại 0
            U_new = np.zeros((self.k, n_samples))
            for j, cluster_idx in enumerate(labels):
                U_new[cluster_idx, j] = 1.0
                
            # Kiểm tra điều kiện hội tụ: |U_new - U_prev| < epsilon
            diff = np.max(np.abs(U_new - U_prev))
            if diff < self.tol and iteration > 0:
                logging.info(f"K-Means hội tụ tại vòng lặp thứ {iteration + 1}.")
                break
                
            U_prev = U_new.copy()
            
            # Cập nhật vector trọng tâm: v_i = sum(m_ij * x_j) / sum(m_ij)
            for c_idx in range(self.k):
                members = X[labels == c_idx]
                if len(members) > 0:
                    self.centroids[c_idx] = np.mean(members, axis=0)
                    
        self.labels_ = labels
        # Tính tổng bình phương khoảng cách nội cụm (Inertia)
        self.inertia_ = sum(np.sum((X[labels == c] - self.centroids[c]) ** 2) for c in range(self.k))
        return self

    def predict(self, X):
        distances = np.zeros((len(X), self.k))
        for c_idx in range(self.k):
            distances[:, c_idx] = np.linalg.norm(X - self.centroids[c_idx], axis=1)
        return np.argmin(distances, axis=1)

class KohonenSOM:
    """
    Cài đặt Mạng nơ-ron tự tổ chức Kohonen (Self-Organizing Map - SOM) theo slide Bài 8:
    - Mảng 2 chiều kích thước map_x * map_y.
    - Trọng số nơ-ron w_ij khởi tạo ngẫu nhiên.
    - Tìm Nơ-ron chiến thắng BMU (Best Matching Unit) có khoảng cách Euclid nhỏ nhất.
    - Cập nhật trọng số trong bán kính lân cận N_c(t):
      w_ijk(t+1) = w_ijk(t) + alpha(t) * [x_k(t) - w_ijk(t)]
    - Hệ số học alpha(t) và bán kính N_c(t) giảm dần theo thời gian.
    """
    def __init__(self, map_x=4, map_y=4, n_epochs=50, initial_alpha=0.2, random_state=42):
        self.map_x = map_x
        self.map_y = map_y
        self.n_epochs = n_epochs
        self.initial_alpha = initial_alpha
        self.random_state = random_state
        self.weights = None

    def fit(self, X):
        np.random.seed(self.random_state)
        n_samples, n_features = X.shape
        
        # Khởi tạo trọng số ngẫu nhiên cho mảng 2 chiều (slide 16-17)
        self.weights = np.random.uniform(0.4, 0.6, (self.map_x, self.map_y, n_features))
        
        alpha = self.initial_alpha
        alpha_decay = alpha / self.n_epochs
        initial_radius = max(self.map_x, self.map_y) / 2.0
        
        for epoch in range(self.n_epochs):
            radius = max(1.0, initial_radius * (1.0 - epoch / self.n_epochs))
            
            # Trộn ngẫu nhiên các mẫu học trong epoch
            indices = np.random.permutation(n_samples)
            for idx in indices:
                x = X[idx]
                
                # Bước 2: Tìm nơ-ron chiến thắng BMU (khoảng cách Euclid nhỏ nhất)
                diff = self.weights - x
                dist = np.sum(diff ** 2, axis=2)
                bmu_x, bmu_y = np.unravel_index(np.argmin(dist), (self.map_x, self.map_y))
                
                # Bước 3: Cập nhật trọng số của nơ-ron chiến thắng và vùng lân cận
                for i in range(self.map_x):
                    for j in range(self.map_y):
                        topo_dist = np.sqrt((i - bmu_x)**2 + (j - bmu_y)**2)
                        if topo_dist <= radius:
                            influence = np.exp(-(topo_dist**2) / (2 * (radius**2)))
                            self.weights[i, j, :] += alpha * influence * (x - self.weights[i, j, :])
                            
            if alpha > 0.01:
                alpha -= alpha_decay
                
        logging.info(f"Hoàn tất huấn luyện mạng Kohonen SOM {self.map_x}x{self.map_y} qua {self.n_epochs} epochs.")
        return self

    def map_samples(self, X):
        mapped_nodes = []
        for x in X:
            diff = self.weights - x
            dist = np.sum(diff ** 2, axis=2)
            bmu = np.unravel_index(np.argmin(dist), (self.map_x, self.map_y))
            mapped_nodes.append(bmu[0] * self.map_y + bmu[1])
        return np.array(mapped_nodes)

def run_clustering_pipeline(normalized_csv_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(normalized_csv_path)
    
    feature_cols = [
        "temperature_2m_mean_minmax",
        "relative_humidity_2m_mean_minmax",
        "surface_pressure_mean_minmax",
        "wind_speed_10m_max_minmax"
    ]
    X = df[feature_cols].values
    
    # 1. Chạy K-Means (K=3 cụm hình thái thời tiết)
    logging.info("Chạy phân cụm K-Means (K=3)...")
    kmeans = CustomKMeans(k=3, max_iter=100, random_state=42)
    kmeans.fit(X)
    df["KMeans_Cluster"] = kmeans.labels_
    
    # Vẽ biểu đồ phân cụm K-Means
    plt.figure(figsize=(10, 6), dpi=150)
    colors = ["#2b5c8f", "#d95f02", "#7570b3"]
    cluster_names = [
        "Cụm 0: Mùa khô nắng nóng (Ẩm thấp, Áp suất cao)",
        "Cụm 1: Mùa mưa rải rác (Nhiệt mát, Gió vừa)",
        "Cụm 2: Mưa bão ngập úng (Ẩm cực cao, Áp suất giảm sâu)"
    ]
    for c in range(3):
        sub = df[df["KMeans_Cluster"] == c]
        plt.scatter(
            sub["temperature_2m_mean"],
            sub["relative_humidity_2m_mean"],
            c=colors[c],
            label=f"{cluster_names[c]} ({len(sub)} ngày)",
            alpha=0.6,
            edgecolors="none",
            s=35
        )
    plt.title("Phân Cụm Hình Thái Khí Tượng TP.HCM Bằng K-Means (K=3)", fontsize=13, fontweight="bold")
    plt.xlabel("Nhiệt độ trung bình (°C)", fontsize=11)
    plt.ylabel("Độ ẩm tương đối (%)", fontsize=11)
    plt.legend(loc="upper left", framealpha=0.9)
    plt.grid(True, linestyle="--", alpha=0.5)
    kmeans_img_path = os.path.join(output_dir, "kmeans_weather_clusters.png")
    plt.tight_layout()
    plt.savefig(kmeans_img_path)
    plt.close()
    
    # 2. Chạy Mạng Kohonen SOM (Lưới 3x3 = 9 nơ-ron)
    logging.info("Chạy gom cụm Mạng Kohonen SOM (3x3)...")
    som = KohonenSOM(map_x=3, map_y=3, n_epochs=30, random_state=42)
    som.fit(X)
    df["Kohonen_Neuron"] = som.map_samples(X)
    
    # Biểu đồ phân bố nơ-ron Kohonen
    neuron_counts = pd.Series(df["Kohonen_Neuron"]).value_counts().sort_index()
    plt.figure(figsize=(8, 5), dpi=150)
    bars = plt.bar(range(9), [neuron_counts.get(i, 0) for i in range(9)], color="#1b9e77", edgecolor="black")
    plt.title("Phân Bố Mẫu Học Trên Bản Đồ Mạng Kohonen SOM (3x3 Nơ-ron)", fontsize=12, fontweight="bold")
    plt.xlabel("Chỉ số Nơ-ron (0 đến 8)", fontsize=11)
    plt.ylabel("Số lượng ngày tương ứng", fontsize=11)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    som_img_path = os.path.join(output_dir, "kohonen_som_distribution.png")
    plt.tight_layout()
    plt.savefig(som_img_path)
    plt.close()
    
    # Tỷ lệ ngập úng theo từng cụm K-Means
    cluster_summary = df.groupby("KMeans_Cluster").agg(
        So_Ngay=("Rain_Flood_Risk", "count"),
        So_Ngay_Ngap=("Rain_Flood_Risk", "sum"),
        Ty_Le_Ngap=("Rain_Flood_Risk", "mean"),
        Nhiet_Do_TB=("temperature_2m_mean", "mean"),
        Do_Am_TB=("relative_humidity_2m_mean", "mean"),
        Ap_Suat_TB=("surface_pressure_mean", "mean")
    ).reset_index()
    
    summary_path = os.path.join(output_dir, "kmeans_cluster_summary.csv")
    cluster_summary.to_csv(summary_path, index=False, encoding="utf-8")
    
    logging.info(f"Đã lưu kết quả gom cụm vào: {summary_path}")
    return {
        "kmeans_inertia": round(float(kmeans.inertia_), 4),
        "cluster_summary": cluster_summary.to_dict(orient="records"),
        "kmeans_img": kmeans_img_path,
        "som_img": som_img_path
    }

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    base_dir = os.path.dirname(os.path.dirname(__file__))
    norm_path = os.path.join(base_dir, "data", "processed", "hcmc_weather_normalized.csv")
    out_dir = os.path.join(base_dir, "outputs")
    res = run_clustering_pipeline(norm_path, out_dir)
    print("\n=== KET QUA GOM CUM K-MEANS & KOHONEN SOM ===")
    print("Tong ket cac cum K-Means:")
    for c in res["cluster_summary"]:
        print(f"  Cụm {c['KMeans_Cluster']}: {c['So_Ngay']} ngày, Tỷ lệ ngập: {c['Ty_Le_Ngap']*100:.1f}%, Nhiệt độ TB: {c['Nhiet_Do_TB']:.1f}°C, Độ ẩm: {c['Do_Am_TB']:.1f}%")

if __name__ == "__main__":
    main()
