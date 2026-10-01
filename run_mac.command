#!/usr/bin/env bash
# ======================================================================
# 1-CLICK LAUNCHER CHO MACOS (FINDER DOUBLE-CLICK)
# ĐỒ ÁN MÔN HỌC IE403: KHAI THÁC DỮ LIỆU VÀ TRUYỀN THÔNG XÃ HỘI (UIT)
# NGUYỄN DUY NHIỆM (@DuyNhiemUIT)
# ======================================================================

cd "$(dirname "$0")"

if [ -d "Source" ]; then
    cd Source
fi

chmod +x run_app.sh 2>/dev/null
./run_app.sh
