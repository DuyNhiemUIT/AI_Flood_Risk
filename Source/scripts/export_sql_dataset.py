# -*- coding: utf-8 -*-
"""
Script: export_sql_dataset.py
Tạo tập tin dữ liệu .sql hoàn chỉnh phục vụ yêu cầu nộp bài của Giảng viên:
1. Phiên bản MySQL 8.0 / MariaDB: `hcmc_weather_kdd.sql`
2. Phiên bản SQLite 3 / ANSI SQL: `hcmc_weather_kdd_sqlite.sql`
- Đồng bộ chuẩn xác 100% tên cột PascalCase và các ngưỡng bin theo `preprocessing.py`.
- Tự động đồng bộ sang cả `data/` và `Source/data/`.
"""

import os
import shutil
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
raw_path = os.path.join(BASE_DIR, "data", "raw", "hcmc_weather_2020_2026.csv")
disc_path = os.path.join(BASE_DIR, "data", "processed", "hcmc_weather_discrete.csv")

df_raw = pd.read_csv(raw_path)
df_disc = pd.read_csv(disc_path)

# ==============================================================================
# 1. TẠO FILE MYSQL / MARIADB: hcmc_weather_kdd.sql
# ==============================================================================
sql_lines = []
sql_lines.append("- ======================================================================")
sql_lines.append("- CƠ SỞ DỮ LIỆU KHÍ TƯỢNG VÀ DỰ BÁO NGUY CƠ MƯA NGẬP TP. HỒ CHÍ MINH")
sql_lines.append("- ĐỒ ÁN MÔN HỌC: IE403 - KHAI THÁC DỮ LIỆU VÀ TRUYỀN THÔNG XÃ HỘI")
sql_lines.append("- KHOA HỆ THỐNG THÔNG TIN - TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN (UIT)")
sql_lines.append("- SINH VIÊN: NGUYỄN DUY NHIỆM  - LỚP IE403.P11")
sql_lines.append("- GIẢNG VIÊN HƯỚNG DẪN: ThS. MAI XUÂN HÙNG")
sql_lines.append("- HỆ QUẢN TRỊ: MySQL 8.0+ / MariaDB 10.x (InnoDB Engine, utf8mb4)")
sql_lines.append("- ======================================================================\n")

sql_lines.append("CREATE DATABASE IF NOT EXISTS `hcmc_flood_kdd` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
sql_lines.append("USE `hcmc_flood_kdd`;\n")

sql_lines.append("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
sql_lines.append("- BẢNG 1: DỮ LIỆU KHÍ TƯỢNG ĐO ĐẠC ĐỊNH LƯỢNG (RAW WEATHER OBSERVATIONS)")
sql_lines.append("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
sql_lines.append("DROP TABLE IF EXISTS `hcmc_weather_raw`;")
sql_lines.append("""CREATE TABLE `hcmc_weather_raw` (
    `date` DATE NOT NULL COMMENT 'Ngày quan trắc khí quyển (YYYY-MM-DD)',
    `temperature_2m_max` DECIMAL(5,2) COMMENT 'Nhiệt độ cao nhất ngày (°C)',
    `temperature_2m_min` DECIMAL(5,2) COMMENT 'Nhiệt độ thấp nhất ngày (°C)',
    `temperature_2m_mean` DECIMAL(5,2) NOT NULL COMMENT 'Nhiệt độ trung bình ngày (°C)',
    `relative_humidity_2m_mean` DECIMAL(5,2) NOT NULL COMMENT 'Độ ẩm tương đối trung bình (%)',
    `precipitation_sum` DECIMAL(6,2) NOT NULL COMMENT 'Tổng lượng mưa tích lũy 24h (mm)',
    `precipitation_hours` DECIMAL(4,1) NOT NULL COMMENT 'Số giờ có mưa trong ngày (h)',
    `surface_pressure_mean` DECIMAL(6,2) NOT NULL COMMENT 'Áp suất khí quyển bề mặt (hPa)',
    `wind_speed_10m_max` DECIMAL(5,2) NOT NULL COMMENT 'Vận tốc gió cực đại ở độ cao 10m (km/h)',
    `wind_direction_10m_dominant` INT NOT NULL COMMENT 'Hướng gió thịnh hành (0-360 độ)',
    `dew_point_2m_mean` DECIMAL(5,2) COMMENT 'Điểm sương trung bình (°C)',
    `Rain_Flood_Risk` TINYINT(1) NOT NULL COMMENT 'Nhãn quyết định: 1 - Nguy cơ ngập cao, 0 - An toàn',
    PRIMARY KEY (`date`),
    INDEX `idx_flood_risk` (`Rain_Flood_Risk`),
    INDEX `idx_humidity` (`relative_humidity_2m_mean`),
    INDEX `idx_pressure` (`surface_pressure_mean`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Dữ liệu thời tiết thô ECMWF ERA5 2020-2026';\n""")

sql_lines.append("LOCK TABLES `hcmc_weather_raw` WRITE;")
sql_lines.append("INSERT INTO `hcmc_weather_raw` VALUES")

raw_values = []
for _, row in df_raw.iterrows:
    vals = (
        f"('{row['date']}', {row['temperature_2m_max']:.2f}, {row['temperature_2m_min']:.2f}, "
        f"{row['temperature_2m_mean']:.2f}, {row['relative_humidity_2m_mean']:.2f}, "
        f"{row['precipitation_sum']:.2f}, {row['precipitation_hours']:.1f}, "
        f"{row['surface_pressure_mean']:.2f}, {row['wind_speed_10m_max']:.2f}, "
        f"{int(row['wind_direction_10m_dominant'])}, {row['dew_point_2m_mean']:.2f}, "
        f"{int(row['Rain_Flood_Risk'])})"
    )
    raw_values.append(vals)

sql_lines.append(",\n".join(raw_values) + ";")
sql_lines.append("UNLOCK TABLES;\n")

sql_lines.append("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
sql_lines.append("- BẢNG 2: DỮ LIỆU KHÍ TƯỢNG RỜI RẠC HÓA PHỤC VỤ KHAI PHÁ TRI THỨC KDD")
sql_lines.append("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
sql_lines.append("DROP TABLE IF EXISTS `hcmc_weather_discrete`;")
sql_lines.append("""CREATE TABLE `hcmc_weather_discrete` (
    `date` DATE NOT NULL,
    `NhietDo` VARCHAR(20) NOT NULL COMMENT 'Mức nhiệt độ (Lanh <= 26, Mat 26-30, Nong > 30)',
    `DoAm` VARCHAR(20) NOT NULL COMMENT 'Mức độ ẩm (BinhThuong <= 75%, Cao > 75%)',
    `ApSuat` VARCHAR(20) NOT NULL COMMENT 'Mức áp suất (Thap <= 1008, TB 1008-1012, Cao > 1012)',
    `Gio` VARCHAR(20) NOT NULL COMMENT 'Vận tốc gió (Yeu <= 15 km/h, Manh > 15 km/h)',
    `HuongGio` VARCHAR(20) NOT NULL COMMENT 'Hướng gió thịnh hành (TayNam, DongBac, Khac)',
    `BienDoNhiet` VARCHAR(20) NOT NULL COMMENT 'Biên độ nhiệt ngày đêm (Hep <= 7, Rong > 7)',
    `Rain_Flood_Risk` TINYINT(1) NOT NULL COMMENT 'Nhãn quyết định: 1 - Nguy cơ ngập, 0 - An toàn',
    PRIMARY KEY (`date`),
    INDEX `idx_disc_risk` (`Rain_Flood_Risk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Dữ liệu rời rạc hóa phục vụ Rough Set & Cây quyết định ID3';\n""")

sql_lines.append("LOCK TABLES `hcmc_weather_discrete` WRITE;")
sql_lines.append("INSERT INTO `hcmc_weather_discrete` VALUES")

disc_values = []
for _, row in df_disc.iterrows:
    vals = (
        f"('{row['date']}', '{row['NhietDo']}', '{row['DoAm']}', "
        f"'{row['ApSuat']}', '{row['Gio']}', '{row['HuongGio']}', "
        f"'{row['BienDoNhiet']}', {int(row['Rain_Flood_Risk'])})"
    )
    disc_values.append(vals)

sql_lines.append(",\n".join(disc_values) + ";")
sql_lines.append("UNLOCK TABLES;\n")

out_mysql = os.path.join(BASE_DIR, "data", "hcmc_weather_kdd.sql")
with open(out_mysql, "w", encoding="utf-8") as f:
    f.write("\n".join(sql_lines))

print(f"Generated MySQL script: {out_mysql} ({os.path.getsize(out_mysql)/1024:.2f} KB)")

# ==============================================================================
# 2. TẠO FILE SQLITE / ANSI SQL: hcmc_weather_kdd_sqlite.sql
# ==============================================================================
sqlite_lines = []
sqlite_lines.append("- ======================================================================")
sqlite_lines.append("- CƠ SỞ DỮ LIỆU KHÍ TƯỢNG VÀ DỰ BÁO NGUY CƠ MƯA NGẬP TP. HỒ CHÍ MINH")
sqlite_lines.append("- HỆ QUẢN TRỊ: SQLite 3 / ANSI SQL Standard Compatible")
sqlite_lines.append("- CÁCH NẠP DỮ LIỆU: sqlite3 hcmc_flood.db < hcmc_weather_kdd_sqlite.sql")
sqlite_lines.append("- ======================================================================\n")

sqlite_lines.append("PRAGMA foreign_keys = ON;\n")

sqlite_lines.append("DROP TABLE IF EXISTS hcmc_weather_raw;")
sqlite_lines.append("""CREATE TABLE hcmc_weather_raw (
    date TEXT NOT NULL PRIMARY KEY,
    temperature_2m_max REAL,
    temperature_2m_min REAL,
    temperature_2m_mean REAL NOT NULL,
    relative_humidity_2m_mean REAL NOT NULL,
    precipitation_sum REAL NOT NULL,
    precipitation_hours REAL NOT NULL,
    surface_pressure_mean REAL NOT NULL,
    wind_speed_10m_max REAL NOT NULL,
    wind_direction_10m_dominant INTEGER NOT NULL,
    dew_point_2m_mean REAL,
    Rain_Flood_Risk INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_raw_flood_risk ON hcmc_weather_raw (Rain_Flood_Risk);
CREATE INDEX IF NOT EXISTS idx_raw_humidity ON hcmc_weather_raw (relative_humidity_2m_mean);
CREATE INDEX IF NOT EXISTS idx_raw_pressure ON hcmc_weather_raw (surface_pressure_mean);
""")

sqlite_lines.append("BEGIN TRANSACTION;")
for val in raw_values:
    sqlite_lines.append(f"INSERT INTO hcmc_weather_raw VALUES {val};")
sqlite_lines.append("COMMIT;\n")

sqlite_lines.append("DROP TABLE IF EXISTS hcmc_weather_discrete;")
sqlite_lines.append("""CREATE TABLE hcmc_weather_discrete (
    date TEXT NOT NULL PRIMARY KEY,
    NhietDo TEXT NOT NULL,
    DoAm TEXT NOT NULL,
    ApSuat TEXT NOT NULL,
    Gio TEXT NOT NULL,
    HuongGio TEXT NOT NULL,
    BienDoNhiet TEXT NOT NULL,
    Rain_Flood_Risk INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_disc_risk ON hcmc_weather_discrete (Rain_Flood_Risk);
""")

sqlite_lines.append("BEGIN TRANSACTION;")
for val in disc_values:
    sqlite_lines.append(f"INSERT INTO hcmc_weather_discrete VALUES {val};")
sqlite_lines.append("COMMIT;\n")

out_sqlite = os.path.join(BASE_DIR, "data", "hcmc_weather_kdd_sqlite.sql")
with open(out_sqlite, "w", encoding="utf-8") as f:
    f.write("\n".join(sqlite_lines))

print(f"Generated SQLite script: {out_sqlite} ({os.path.getsize(out_sqlite)/1024:.2f} KB)")

# Kiểm tra cú pháp trực tiếp bằng sqlite3 in-memory
conn = sqlite3.connect(":memory:")
with open(out_sqlite, "r", encoding="utf-8") as f:
    conn.executescript(f.read)
c_raw = conn.execute("SELECT count(*) FROM hcmc_weather_raw").fetchone[0]
c_disc = conn.execute("SELECT count(*) FROM hcmc_weather_discrete").fetchone[0]
conn.close
print(f"Verified SQLite load successfully: raw={c_raw} rows, discrete={c_disc} rows")

# ==============================================================================
# 3. ĐỒNG BỘ SANG THƯ MỤC SOURCE/DATA
# ==============================================================================
src_data_dir = os.path.join(BASE_DIR, "Source", "data")
os.makedirs(src_data_dir, exist_ok=True)
shutil.copy2(out_mysql, os.path.join(src_data_dir, "hcmc_weather_kdd.sql"))
shutil.copy2(out_sqlite, os.path.join(src_data_dir, "hcmc_weather_kdd_sqlite.sql"))
print("Synchronized SQL files to Source/data/ successfully!")
