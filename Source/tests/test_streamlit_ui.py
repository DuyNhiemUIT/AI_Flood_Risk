"""
Module: test_streamlit_ui.py
Mục đích: Bộ kiểm thử tự động UI/UX và logic điều hướng Streamlit app với Kiến trúc Dual-Mode:
- Kiểm tra độ đầy đủ, chuẩn mực học thuật của toàn bộ nhãn nút bấm (UX Academic Labels Check).
- Kiểm tra tính đầy đủ và logic của thanh điều hướng 5 bước KDD (Top Toolbar) và Sidebar trong Mode 2.
- Kiểm tra tính hợp lệ của cấu trúc KDD_STEP_CONFIG.
- Kiểm tra khởi chạy AppTest trên Streamlit và chế độ mặc định (Citizen Live Portal).
- Kiểm tra các thành phần của Mode 1 (Citizen Live Portal): Thời tiết thực tế, cảnh báo rủi ro, lộ trình an toàn, SOS và xác nhận khối CTA học thuật đã được loại bỏ hoàn toàn.
- Kiểm tra chuyển đổi 2 chiều mượt mà giữa Citizen Live Portal và Research Lab.
- Kiểm tra tương tác thực tế của các nút bấm điều hướng (Top Toolbar 5 bước và Sidebar quick-jump) trong Mode 2.
- Kiểm tra luồng dự báo thời gian thực và kịch bản presets tại Bước 5.
"""

import os
import sys
import re
import pytest
from streamlit.testing.v1 import AppTest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_FILE = os.path.join(BASE_DIR, "app", "streamlit_app.py")

EXPECTED_STEP_LABELS = [
    "1. Thu Thập Dữ Liệu",
    "2. Tiền Xử Lý & Gom Cụm",
    "3. Rút Gọn Tập Thô Pawlak",
    "4. Đánh Giá Hiệu Năng",
    "5. Dự Báo & Cảnh Báo"
]

EXPECTED_ACTION_LABELS = [
    "⚡ Thực hiện phân tích EDA & Tính ma trận Pearson",
    "⚡ Chạy thuật toán gom cụm K-Means (K=",
    "⚡ Tính hệ số phụ thuộc & Trích xuất luật Pawlak",
    "⚡ Kiểm định hiệu năng trên tập Test (487 ngày)",
    "🚀 Dự báo nguy cơ ngập & Cảnh báo điểm đen UIT",
    "🚨 1. Mưa bão cực đoan (Test báo động)",
    "☀️ 2. Mùa khô nắng ráo (Test an toàn)",
    "🌐 3. Cập nhật dữ liệu thực tế (Open-Meteo API)",
    "🔄 Làm mới thời tiết thực tế"
]

MODE_CITIZEN = "🛡️ Cổng Giám Sát Ngập Cục Bộ Khu Vực UIT & Thủ Đức (UIT & Thu Duc Flood Portal)"
MODE_RESEARCH = "🔬 Báo Cáo & Phòng Nghiên Cứu KDD (Research Lab)"

def test_button_label_conciseness():
    """Kiểm tra toàn bộ nút bấm trong app (cả chuỗi tĩnh và f-string) đều chuẩn mực, rõ nghĩa."""
    with open(APP_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Tìm tất cả các nhãn nút bấm st.button và st.sidebar.button
    button_labels = re.findall(r'st(?:\.sidebar)?\.button\(\s*(?:f)?["\']([^"\']+)["\']', content)
    
    assert len(button_labels) > 0, "Phải có ít nhất 1 nút button được tìm thấy"
    
    # Mẫu thay thế giả lập các biến f-string
    sample_replacements = {
        "{k_choice}": "3",
        "{cur_step}": "1",
        "{i}": "1",
        "{name}": "Rút Gọn Tập Thô Pawlak"
    }
    
    for raw_lbl in button_labels:
        lbl = raw_lbl
        for var, val in sample_replacements.items():
            lbl = lbl.replace(var, val)
        # Chuẩn nhãn: tất cả các nút bấm <= 65 ký tự
        assert len(lbl) <= 65, f"Nút '{raw_lbl}' sau khi điền '{lbl}' quá dài ({len(lbl)} ký tự > 65 ký tự)!"

    # Xác nhận không còn nút CTA 'Khám phá quy trình' trong bất kỳ nút nào
    assert not any("Khám phá quy trình" in lbl for lbl in button_labels), (
        "Nút CTA 'Khám phá quy trình' không được tồn tại trong app"
    )

    # Kiểm tra cả 5 nhãn bước KDD
    for step_lbl in EXPECTED_STEP_LABELS:
        assert len(step_lbl) <= 65, f"Nhãn bước '{step_lbl}' vượt quá 65 ký tự!"

def test_action_buttons_exact_conciseness():
    """Kiểm tra nhãn đầy đủ, chính xác của các nút thực thi nghiệp vụ (Action CTAs) ở cả 2 mode."""
    with open(APP_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    for action_lbl in EXPECTED_ACTION_LABELS:
        assert action_lbl in content, f"Thiếu nút hành động '{action_lbl}' trong streamlit_app.py"

    # Xác nhận khối CTA học thuật không còn tồn tại trong streamlit_app.py
    assert "🔬 Khám phá quy trình Khai phá tri thức KDD & Mô hình AI" not in content, (
        "Nút CTA 'Khám phá quy trình' không được xuất hiện trong streamlit_app.py"
    )
    assert "citizen_cta_switch" not in content, (
        "Khóa 'citizen_cta_switch' không được xuất hiện trong streamlit_app.py"
    )
    assert "citizen-cta-card" not in content, (
        "Class CSS 'citizen-cta-card' không được xuất hiện trong streamlit_app.py"
    )
    assert "DÀNH CHO GIẢNG VIÊN & HỘI ĐỒNG BẢO VỆ" not in content, (
        "Banner 'DÀNH CHO GIẢNG VIÊN' không được xuất hiện trong streamlit_app.py"
    )
    assert "Khám phá chi tiết toàn bộ Chu trình Khám phá Tri thức KDD" not in content, (
        "Mô tả CTA KDD không được xuất hiện trong streamlit_app.py"
    )

    # Xác nhận khối thử nghiệm kịch bản giả lập ở Chế độ 1 không còn tồn tại trong streamlit_app.py
    assert "sim_storm_btn" not in content, (
        "Khóa nút 'sim_storm_btn' không được xuất hiện trong streamlit_app.py"
    )
    assert "sim_dry_btn" not in content, (
        "Khóa nút 'sim_dry_btn' không được xuất hiện trong streamlit_app.py"
    )
    assert "Thử nghiệm kịch bản giả lập" not in content, (
        "Expander 'Thử nghiệm kịch bản giả lập' không được xuất hiện trong streamlit_app.py"
    )

def test_kdd_step_config_structure():
    """Kiểm tra cấu trúc và tính nhất quán của KDD_STEP_CONFIG và các hàm điều hướng."""
    with open(APP_FILE, "r", encoding="utf-8") as f:
        source = f.read()
    
    assert "KDD_STEP_CONFIG" in source
    assert "render_top_nav" in source
    assert "render_dynamic_stepper" in source
    assert "render_bottom_nav" not in source

def test_streamlit_apptest_execution():
    """Kiểm tra khởi chạy Streamlit app qua AppTest không gặp Exception và khởi tạo đúng chế độ mặc định."""
    at = AppTest.from_file(APP_FILE, default_timeout=25).run()
    assert len(at.exception) == 0, f"AppTest gặp lỗi: {[str(e) for e in at.exception]}"
    assert at.session_state["app_mode"] == MODE_CITIZEN
    assert at.session_state["active_kdd_step"] == 1

def test_citizen_portal_features():
    """Kiểm tra đầy đủ các tính năng của Mode 1: Cổng Cảnh Báo Người Dân."""
    at = AppTest.from_file(APP_FILE, default_timeout=25).run()
    assert at.session_state["app_mode"] == MODE_CITIZEN
    
    # 1. Kiểm tra sự hiện diện của nút Làm mới thời tiết thực tế
    refresh_btns = [b for b in at.button if "🔄 Làm mới thời tiết thực tế" in b.label]
    assert len(refresh_btns) == 1, "Nút làm mới thời tiết thực tế phải có mặt trong Citizen Portal"
    
    # 2. Click làm mới thời tiết thực tế
    refresh_btns[0].click().run()
    assert len(at.exception) == 0
    assert "citizen_weather_raw" in at.session_state
    
    # 2b. Kiểm tra chỉ báo kết nối Live API và siêu dữ liệu telemetry
    md_texts = " ".join([m.value for m in at.markdown])
    assert "live-indicator-container" in md_texts
    assert "live-signal-badge" in md_texts
    assert ("TÍN HIỆU TRỰC TUYẾN" in md_texts or "DỰ PHÒNG NGOẠI TUYẾN" in md_texts)
    assert "Open-Meteo WMO / ECMWF ERA5 Real-time API" in md_texts
    assert "10.823°N, 106.630°E" in md_texts
    assert not any("Thông số kỹ thuật Telemetry API" in e.label for e in at.expander), "Citizen Portal không chứa expander Telemetry API kỹ thuật"
    assert "https://api.open-meteo.com/v1/forecast" in md_texts
    
    # 3. Kiểm tra tiện ích tra cứu lộ trình an toàn có selectbox và duyệt tất cả các điểm xuất phát
    route_select = at.selectbox(key="route_origin_select")
    assert route_select is not None
    expected_origins = [
        "Quận 1", "Quận Bình Thạnh", "KTX Khu B (ĐHQG)",
        "Chợ Thủ Đức", "Ngã tư Thủ Đức", "Quận Gò Vấp"
    ]
    for origin in expected_origins:
        assert origin in route_select.options
        route_select.select(origin).run()
        assert len(at.exception) == 0
        
    # 4. Kiểm tra xác nhận kịch bản giả lập đã được loại bỏ hoàn toàn khỏi Mode 1 (thuần dữ liệu thực tế)
    with pytest.raises(KeyError):
        at.button(key="sim_storm_btn")
    with pytest.raises(KeyError):
        at.button(key="sim_dry_btn")
    assert not any("Thử nghiệm kịch bản giả lập" in e.label for e in at.expander)
    sim_btns_m1 = [b for b in at.button if "Thử kịch bản" in b.label]
    assert len(sim_btns_m1) == 0, "Không được có nút thử kịch bản giả lập nào trong Citizen Portal"
    
    # 5. Kiểm tra xác nhận khối CTA và nút citizen_cta_switch đã được loại bỏ hoàn toàn khỏi Mode 1
    with pytest.raises(KeyError):
        at.button(key="citizen_cta_switch")
    cta_btns = [b for b in at.button if "Khám phá quy trình Khai phá tri thức KDD" in b.label]
    assert len(cta_btns) == 0, "Nút CTA chuyển sang Mode 2 không được xuất hiện trong Citizen Portal"
    markdown_contents = [m.value for m in at.markdown]
    assert not any("citizen-cta-card" in m for m in markdown_contents), "Khối citizen-cta-card không được xuất hiện trong Citizen Portal"
    assert not any("DÀNH CHO GIẢNG VIÊN & HỘI ĐỒNG BẢO VỆ" in m for m in markdown_contents), "Banner hội đồng bảo vệ không được xuất hiện trong Citizen Portal"
    assert not any("Khám phá chi tiết toàn bộ Chu trình" in m for m in markdown_contents), "Mô tả KDD không được xuất hiện trong Citizen Portal"
    assert not any("66 luật tiền định 100%" in m for m in markdown_contents), "Nội dung luật học thuật không được xuất hiện trong nội dung chính Mode 1"
    
    # 6. Kiểm tra radio chuyển chế độ sẵn sàng trong Sidebar
    assert at.sidebar.radio(key="app_mode_radio") is not None, "Radio chuyển chế độ phải nằm trong Sidebar"
    assert at.sidebar.radio(key="app_mode_radio").options == [MODE_CITIZEN, MODE_RESEARCH]
    assert at.sidebar.markdown[0].value == "---", "Thanh phân cách phải nằm ngay dưới radio chuyển chế độ trong Sidebar"
    with pytest.raises(KeyError):
        at.main.radio(key="app_mode_radio")

def test_mode_switching_bidirectional():
    """Kiểm tra khả năng chuyển đổi hai chiều linh hoạt giữa Mode 1 và Mode 2 qua cả radio và sidebar."""
    at = AppTest.from_file(APP_FILE, default_timeout=25).run()
    assert at.session_state["app_mode"] == MODE_CITIZEN
    
    # 1. Chuyển sang Mode 2 qua radio trong Sidebar
    at.sidebar.radio(key="app_mode_radio").set_value(MODE_RESEARCH).run()
    assert len(at.exception) == 0
    assert at.session_state["app_mode"] == MODE_RESEARCH
    assert at.sidebar.radio(key="app_mode_radio").value == MODE_RESEARCH
    assert at.button(key="top_step_1") is not None
    
    # 2. Chuyển ngược lại Mode 1 qua radio trong Sidebar
    at.sidebar.radio(key="app_mode_radio").set_value(MODE_CITIZEN).run()
    assert len(at.exception) == 0
    assert at.session_state["app_mode"] == MODE_CITIZEN
    assert at.sidebar.radio(key="app_mode_radio").value == MODE_CITIZEN
    refresh_btns = [b for b in at.button if "🔄 Làm mới thời tiết thực tế" in b.label]
    assert len(refresh_btns) == 1

    # 3. Chuyển sang Mode 2 qua Sidebar radio switcher
    at.sidebar.radio(key="app_mode_radio").set_value(MODE_RESEARCH).run()
    assert len(at.exception) == 0
    assert at.session_state["app_mode"] == MODE_RESEARCH
    assert at.sidebar.radio(key="app_mode_radio").value == MODE_RESEARCH
    assert at.button(key="top_step_1") is not None

    # 4. Chuyển ngược lại Mode 1 qua Sidebar radio switcher
    at.sidebar.radio(key="app_mode_radio").set_value(MODE_CITIZEN).run()
    assert len(at.exception) == 0
    assert at.session_state["app_mode"] == MODE_CITIZEN
    assert at.sidebar.radio(key="app_mode_radio").value == MODE_CITIZEN

def test_navigation_interactive_clicks():
    """Kiểm tra click tương tác thực tế trên các nút điều hướng Top Toolbar 5 bước và CTA từng bước trong Mode 2."""
    at = AppTest.from_file(APP_FILE, default_timeout=25).run()
    # Chuyển sang Mode 2: Research Lab qua Sidebar radio
    at.sidebar.radio(key="app_mode_radio").set_value(MODE_RESEARCH).run()
    assert len(at.exception) == 0
    assert at.session_state["app_mode"] == MODE_RESEARCH
    assert at.session_state["active_kdd_step"] == 1
    
    # 1. Xác nhận các nút điều hướng cũ không tồn tại
    with pytest.raises(KeyError):
        at.button(key="top_next")
    with pytest.raises(KeyError):
        at.button(key="top_prev")
    with pytest.raises(KeyError):
        at.button(key="top_restart")
        
    # Xác nhận nhãn nút chuẩn và kiểu hiển thị (primary cho bước hiện tại, secondary cho bước khác)
    assert at.button(key="top_step_1").label == EXPECTED_STEP_LABELS[0]
    assert at.button(key="top_step_1").proto.type == "primary"
    assert at.button(key="top_step_2").label == EXPECTED_STEP_LABELS[1]
    assert at.button(key="top_step_2").proto.type == "secondary"
    assert at.button(key="top_step_3").label == EXPECTED_STEP_LABELS[2]
    assert at.button(key="top_step_3").proto.type == "secondary"
    assert at.button(key="top_step_4").label == EXPECTED_STEP_LABELS[3]
    assert at.button(key="top_step_4").proto.type == "secondary"
    assert at.button(key="top_step_5").label == EXPECTED_STEP_LABELS[4]
    assert at.button(key="top_step_5").proto.type == "secondary"

    # Kiểm tra nút CTA ở Bước 1
    eda_buttons = [b for b in at.button if "⚡ Thực hiện phân tích EDA & Tính ma trận Pearson" in b.label]
    assert len(eda_buttons) == 1, "Nút CTA EDA Bước 1 không hiển thị đúng nhãn"
        
    # 2. Click trực tiếp nút Bước 2 trên Top Toolbar ('2. Tiền Xử Lý & Gom Cụm')
    top_step_2 = at.button(key="top_step_2")
    assert top_step_2 is not None
    top_step_2.click().run()
    assert len(at.exception) == 0
    assert at.session_state["active_kdd_step"] == 2
    assert at.button(key="top_step_1").proto.type == "secondary"
    assert at.button(key="top_step_2").proto.type == "primary"
    assert at.button(key="top_step_2").label == EXPECTED_STEP_LABELS[1]
    km_buttons = [b for b in at.button if "⚡ Chạy thuật toán gom cụm K-Means" in b.label]
    assert len(km_buttons) == 1, "Nút CTA K-Means Bước 2 không hiển thị đúng nhãn"
    
    # 3. Click trực tiếp nút Bước 3 trên Top Toolbar ('3. Rút Gọn Tập Thô Pawlak')
    top_step_3 = at.button(key="top_step_3")
    assert top_step_3 is not None
    top_step_3.click().run()
    assert len(at.exception) == 0
    assert at.session_state["active_kdd_step"] == 3
    assert at.button(key="top_step_3").proto.type == "primary"
    assert at.button(key="top_step_2").proto.type == "secondary"
    rs_buttons = [b for b in at.button if "⚡ Tính hệ số phụ thuộc & Trích xuất luật Pawlak" in b.label]
    assert len(rs_buttons) == 1, "Nút CTA Rough Set Bước 3 không hiển thị đúng nhãn"
    
    # 4. Click trực tiếp nút Bước 4 trên Top Toolbar ('4. Đánh Giá Hiệu Năng')
    top_step_4 = at.button(key="top_step_4")
    assert top_step_4 is not None
    top_step_4.click().run()
    assert len(at.exception) == 0
    assert at.session_state["active_kdd_step"] == 4
    assert at.button(key="top_step_4").proto.type == "primary"
    assert at.button(key="top_step_3").proto.type == "secondary"
    eval_buttons = [b for b in at.button if "⚡ Kiểm định hiệu năng trên tập Test (487 ngày)" in b.label]
    assert len(eval_buttons) == 1, "Nút CTA Đánh giá Bước 4 không hiển thị đúng nhãn"
    
    # 5. Click trực tiếp nút Bước 5 trên Top Toolbar ('5. Dự Báo & Cảnh Báo')
    top_step_5 = at.button(key="top_step_5")
    assert top_step_5 is not None
    top_step_5.click().run()
    assert len(at.exception) == 0
    assert at.session_state["active_kdd_step"] == 5
    assert at.button(key="top_step_5").proto.type == "primary"
    assert at.button(key="top_step_4").proto.type == "secondary"
    pred_buttons = [b for b in at.button if "🚀 Dự báo nguy cơ ngập & Cảnh báo điểm đen UIT" in b.label]
    assert len(pred_buttons) == 1, "Nút CTA Dự báo Bước 5 không hiển thị đúng nhãn"
    
    # 6. Click quay lại Bước 1 qua Top Toolbar
    top_step_1 = at.button(key="top_step_1")
    assert top_step_1 is not None
    top_step_1.click().run()
    assert len(at.exception) == 0
    assert at.session_state["active_kdd_step"] == 1
    assert at.button(key="top_step_1").proto.type == "primary"
    assert at.button(key="top_step_5").proto.type == "secondary"
    
    # 7. Kiểm tra điều hướng trực tiếp bằng Top Toolbar sang Bước 3
    top_step_3 = at.button(key="top_step_3")
    assert top_step_3 is not None
    top_step_3.click().run()
    assert len(at.exception) == 0
    assert at.session_state["active_kdd_step"] == 3
    assert at.button(key="top_step_3").proto.type == "primary"

def test_step_5_live_prediction_flow():
    """Kiểm tra luồng tương tác tại Bước 5 (Dự Báo & Cảnh Báo): Presets và CTA Dự báo trong Mode 2."""
    at = AppTest.from_file(APP_FILE, default_timeout=25).run()
    # Chuyển sang Mode 2: Research Lab qua Sidebar radio
    at.sidebar.radio(key="app_mode_radio").set_value(MODE_RESEARCH).run()
    assert len(at.exception) == 0
    # Nhảy sang Bước 5 bằng nút top_step_5
    at.button(key="top_step_5").click().run()
    assert len(at.exception) == 0
    assert at.session_state["active_kdd_step"] == 5
    
    # 1. Xác minh sự hiện diện của đầy đủ 4 nút ở Bước 5 với nhãn học thuật đầy đủ
    step5_labels = [b.label for b in at.button]
    assert "🚨 1. Mưa bão cực đoan (Test báo động)" in step5_labels
    assert "☀️ 2. Mùa khô nắng ráo (Test an toàn)" in step5_labels
    assert "🌐 3. Cập nhật dữ liệu thực tế (Open-Meteo API)" in step5_labels
    assert "🚀 Dự báo nguy cơ ngập & Cảnh báo điểm đen UIT" in step5_labels
    
    # 2. Thử nghiệm kịch bản 1: Mưa bão cực đoan
    storm_btn = [b for b in at.button if "🚨 1. Mưa bão cực đoan (Test báo động)" in b.label][0]
    storm_btn.click().run()
    assert len(at.exception) == 0
    assert at.session_state["weather_input"]["NhietDo"] == "Lanh"
    assert at.session_state["weather_input"]["DoAm"] == "Cao"
    assert at.session_state["weather_input"]["ApSuat"] == "Thap"
    
    # Click nút Dự báo sau kịch bản bão
    pred_btn = [b for b in at.button if "🚀 Dự báo nguy cơ ngập & Cảnh báo điểm đen UIT" in b.label][0]
    pred_btn.click().run()
    assert len(at.exception) == 0
    
    # 3. Thử nghiệm kịch bản 2: Mùa khô nắng ráo
    dry_btn = [b for b in at.button if "☀️ 2. Mùa khô nắng ráo (Test an toàn)" in b.label][0]
    dry_btn.click().run()
    assert len(at.exception) == 0
    assert at.session_state["weather_input"]["NhietDo"] == "Nong"
    assert at.session_state["weather_input"]["DoAm"] == "BinhThuong"
    assert at.session_state["weather_input"]["ApSuat"] == "Cao"
    
    # Click nút Dự báo sau kịch bản khô
    pred_btn = [b for b in at.button if "🚀 Dự báo nguy cơ ngập & Cảnh báo điểm đen UIT" in b.label][0]
    pred_btn.click().run()
    assert len(at.exception) == 0

    # 4. Thử nghiệm kịch bản 3: Cập nhật dữ liệu thực tế (Open-Meteo API)
    live_btn = [b for b in at.button if "🌐 3. Cập nhật dữ liệu thực tế (Open-Meteo API)" in b.label][0]
    live_btn.click().run()
    assert len(at.exception) == 0
    assert "weather_input" in at.session_state
    assert at.session_state["live_raw_info"] is not None
    
    # 5. Kiểm tra chỉ báo kết nối Live API và siêu dữ liệu telemetry tại Bước 5
    md_step5 = " ".join([m.value for m in at.markdown])
    assert "live-indicator-container" in md_step5
    assert "live-signal-badge" in md_step5
    assert "Open-Meteo WMO / ECMWF ERA5 Real-time API" in md_step5
    assert "10.823°N, 106.630°E" in md_step5
    assert any("Thông số kỹ thuật Telemetry API" in e.label for e in at.expander)
    assert "https://api.open-meteo.com/v1/forecast" in md_step5

def test_live_meteo_api_indicator_and_telemetry():
    """Kiểm tra toàn diện chỉ báo tín hiệu kết nối Live Open-Meteo API và thông số Telemetry:
    - Hiệu ứng CSS và cấu trúc container/badge/dot.
    - Đầy đủ 6 nhóm metadata: Trạng thái, Nguồn & Mô hình, Tọa độ trạm, Độ trễ (Latency), Timestamp, Giao thức.
    - Chuyển mạch trạng thái ngoại tuyến khi mô phỏng kịch bản (Fallback).
    - Hiển thị đầy đủ ở cả Mode 1 (Citizen Live Portal) và Mode 2 (Research Lab - Step 5).
    - Khối chi tiết mở rộng (Expander) Thông số kỹ thuật Telemetry API.
    """
    at = AppTest.from_file(APP_FILE, default_timeout=25).run()
    assert at.session_state["app_mode"] == MODE_CITIZEN
    
    # 1. Kiểm tra Mode 1: Chỉ báo trực tuyến ban đầu
    all_md_m1 = " ".join([m.value for m in at.markdown])
    assert "live-indicator-container" in all_md_m1
    assert "live-signal-badge" in all_md_m1
    assert "live-signal-dot" in all_md_m1
    assert ("TÍN HIỆU TRỰC TUYẾN" in all_md_m1 or "DỰ PHÒNG NGOẠI TUYẾN" in all_md_m1)
    assert "Open-Meteo WMO / ECMWF ERA5 Real-time API" in all_md_m1
    assert "10.823°N, 106.630°E" in all_md_m1
    assert "Trạm Tân Sơn Nhất / TP. Thủ Đức" in all_md_m1
    assert "Độ trễ / Phản hồi (Latency):" in all_md_m1
    assert "HTTPS / RESTful JSON / WMO Standard" in all_md_m1
    assert not any("Thông số kỹ thuật Telemetry API" in e.label for e in at.expander), "Citizen Portal không chứa expander Telemetry API"
    assert "https://api.open-meteo.com/v1/forecast" in all_md_m1
    assert "latitude=10.823" in all_md_m1
    assert "longitude=106.630" in all_md_m1
    
    # 2. Kiểm tra Mode 1: Xác nhận khối kịch bản giả lập đã được gỡ bỏ hoàn toàn (thuần Live Telemetry)
    with pytest.raises(KeyError):
        at.button(key="sim_storm_btn")
    with pytest.raises(KeyError):
        at.button(key="sim_dry_btn")
    assert not any("Thử nghiệm kịch bản giả lập" in e.label for e in at.expander)
    sim_btns_live = [b for b in at.button if "Thử kịch bản" in b.label]
    assert len(sim_btns_live) == 0, "Không được có nút thử kịch bản giả lập nào trong Citizen Portal"
    refresh_btn = at.button(key="citizen_refresh_weather")
    assert refresh_btn is not None
    refresh_btn.click().run()
    assert len(at.exception) == 0
    
    # 3. Kiểm tra Mode 2: Chuyển sang Research Lab và vào Bước 5 qua Sidebar radio
    at.sidebar.radio(key="app_mode_radio").set_value(MODE_RESEARCH).run()
    assert len(at.exception) == 0
    at.button(key="top_step_5").click().run()
    assert len(at.exception) == 0
    
    # 4. Bước 5: Kiểm tra chỉ báo tín hiệu hiển thị và kịch bản giả lập chuyển sang offline
    all_md_m2 = " ".join([m.value for m in at.markdown])
    assert "live-indicator-container" in all_md_m2
    assert "Open-Meteo WMO / ECMWF ERA5 Real-time API" in all_md_m2
    assert "10.823°N, 106.630°E" in all_md_m2
    assert any("Thông số kỹ thuật Telemetry API" in e.label for e in at.expander)

    storm_step5 = [b for b in at.button if "🚨 1. Mưa bão cực đoan (Test báo động)" in b.label][0]
    storm_step5.click().run()
    assert len(at.exception) == 0
    all_md_storm_step5 = " ".join([m.value for m in at.markdown])
    assert "🟡 DỰ PHÒNG NGOẠI TUYẾN" in all_md_storm_step5
    assert "live-signal-badge offline" in all_md_storm_step5
    
    # 5. Bước 5: Click nút cập nhật dữ liệu thực tế Live API
    live_btn = [b for b in at.button if "🌐 3. Cập nhật dữ liệu thực tế (Open-Meteo API)" in b.label][0]
    live_btn.click().run()
    assert len(at.exception) == 0
    all_md_live_updated = " ".join([m.value for m in at.markdown])
    assert "live-indicator-container" in all_md_live_updated
    assert any("Thông số kỹ thuật Telemetry API" in e.label for e in at.expander)
    assert "https://api.open-meteo.com/v1/forecast" in all_md_live_updated
    assert at.session_state["live_raw_info"] is not None


def test_mode_specific_headers_and_footer():
    """Kiểm tra sự phân tách rõ ràng giữa Header/Footer của Chế độ Người dân (Mode 1) và Chế độ Nghiên cứu (Mode 2):
    - Mode 1: Top Hero Header mang tính dân sự 100%, không chứa thông tin học thuật/sinh viên.
              Footer có Academic Credits Box chứa thông tin Đồ án, Sinh viên, GVHD và các huy hiệu KDD.
    - Mode 2: Top Hero Header mang tính học thuật, chứa thông tin Đồ án, Sinh viên, GVHD và huy hiệu KDD.
    """
    at = AppTest.from_file(APP_FILE, default_timeout=25).run()
    assert at.session_state["app_mode"] == MODE_CITIZEN
    
    # 1. Kiểm tra Mode 1 (Citizen Live Portal)
    markdown_contents = [m.value for m in at.markdown]
    hero_header_citizen = [m for m in markdown_contents if '<div class="hero-header">' in m]
    assert len(hero_header_citizen) >= 1, "Phải tìm thấy hero-header trong Mode 1"
    hero_text = hero_header_citizen[0]
    
    # Tiêu đề và nội dung công dân
    assert "🌧️ CỔNG CẢNH BÁO MƯA NGẬP ĐÔ THỊ TP. HỒ CHÍ MINH" in hero_text
    assert "Hệ thống giám sát rủi ro ngập úng thời gian thực" in hero_text
    assert "🌐 Dữ liệu Thời gian thực" in hero_text
    assert "📍 Giám sát 4 Điểm đen UIT" in hero_text
    assert "🧭 Hướng dẫn Lộ trình" in hero_text
    assert "🆘 Đường dây nóng Khẩn cấp" in hero_text
    
    # KHÔNG chứa thông tin sinh viên/học thuật ở Top Hero Header
    assert "NGUYỄN DUY NHIỆM" not in hero_text
    assert "24730129" not in hero_text
    assert "ThS. Mai Xuân Hùng" not in hero_text
    assert "Champion: Naive Bayes" not in hero_text
    
    # Footer Mode 1 phải chứa Footer chuẩn mực bản quyền UIT & Đề tài
    footer_notes = [m for m in markdown_contents if '<div class="app-footer-note"' in m]
    assert len(footer_notes) >= 1, "Mode 1 phải có Footer chuẩn mực ở chân trang"
    footer_text = "".join(footer_notes)
    assert "ĐỒ ÁN MÔN HỌC IE403: KHAI THÁC DỮ LIỆU VÀ TRUYỀN THÔNG XÃ HỘI" in footer_text
    assert "Hệ Thống Dự Báo Nguy Cơ Mưa Ngập Cục Bộ Khu Vực UIT & Thủ Đức" in footer_text
    assert "Nguyễn Duy Nhiệm" in footer_text
    assert "DuyNhiemUIT" in footer_text
    assert "ThS. Mai Xuân Hùng" in footer_text
    assert "Bản quyền đồ án © 2026 Khoa Hệ thống Thông tin" in footer_text
    
    # 2. Chuyển sang Mode 2 (Research Lab) qua sidebar radio
    at.sidebar.radio(key="app_mode_radio").set_value(MODE_RESEARCH).run()
    assert len(at.exception) == 0
    assert at.session_state["app_mode"] == MODE_RESEARCH
    
    markdown_contents_m2 = [m.value for m in at.markdown]
    hero_header_research = [m for m in markdown_contents_m2 if '<div class="hero-header">' in m]
    assert len(hero_header_research) >= 1, "Phải tìm thấy hero-header trong Mode 2"
    research_hero_text = hero_header_research[0]
    
    # Mode 2: Hero Header phải chứa đầy đủ thông tin học thuật
    assert "🌧️ HỆ THỐNG DỰ BÁO NGUY CƠ MƯA NGẬP CỤC BỘ KHU VỰC UIT & THỦ ĐỨC" in research_hero_text
    assert "IE403 - KHAI THÁC DỮ LIỆU VÀ TRUYỀN THÔNG XÃ HỘI" in research_hero_text
    assert "NGUYỄN DUY NHIỆM" in research_hero_text
    assert "DuyNhiemUIT" in research_hero_text
    assert "ThS. Mai Xuân Hùng" in research_hero_text
    assert "Champion: Naive Bayes (Laplace)" in research_hero_text
    assert "Recall: 80.33%" in research_hero_text
    assert "CỔNG CẢNH BÁO MƯA NGẬP ĐÔ THỊ" not in research_hero_text
    assert any("Bản quyền đồ án © 2026 Khoa Hệ thống Thông tin" in m for m in markdown_contents_m2)

    # 3. Chuyển ngược lại Mode 1 (Citizen Live Portal) qua sidebar radio
    at.sidebar.radio(key="app_mode_radio").set_value(MODE_CITIZEN).run()
    assert len(at.exception) == 0
    assert at.session_state["app_mode"] == MODE_CITIZEN
    
    markdown_contents_m1_ret = [m.value for m in at.markdown]
    hero_ret = [m for m in markdown_contents_m1_ret if '<div class="hero-header">' in m][0]
    assert "🌧️ CỔNG CẢNH BÁO MƯA NGẬP ĐÔ THỊ TP. HỒ CHÍ MINH" in hero_ret
    assert "NGUYỄN DUY NHIỆM" not in hero_ret
    assert any("Bản quyền đồ án © 2026 Khoa Hệ thống Thông tin" in m for m in markdown_contents_m1_ret)

    # 4. Chuyển sang Mode 2 qua Sidebar radio switcher
    at.sidebar.radio(key="app_mode_radio").set_value(MODE_RESEARCH).run()
    assert len(at.exception) == 0
    assert at.session_state["app_mode"] == MODE_RESEARCH
    markdown_contents_m2_sb = [m.value for m in at.markdown]
    hero_sb = [m for m in markdown_contents_m2_sb if '<div class="hero-header">' in m][0]
    assert "NGUYỄN DUY NHIỆM" in hero_sb
    assert any("Bản quyền đồ án © 2026 Khoa Hệ thống Thông tin" in m for m in markdown_contents_m2_sb)

    # 5. Chuyển ngược lại Mode 1 qua Sidebar radio switcher
    at.sidebar.radio(key="app_mode_radio").set_value(MODE_CITIZEN).run()
    assert len(at.exception) == 0
    assert at.session_state["app_mode"] == MODE_CITIZEN
    markdown_contents_m1_final = [m.value for m in at.markdown]
    hero_final = [m for m in markdown_contents_m1_final if '<div class="hero-header">' in m][0]
    assert "🌧️ CỔNG CẢNH BÁO MƯA NGẬP ĐÔ THỊ TP. HỒ CHÍ MINH" in hero_final
    assert "NGUYỄN DUY NHIỆM" not in hero_final
    assert any("Bản quyền đồ án © 2026 Khoa Hệ thống Thông tin" in m for m in markdown_contents_m1_final)

def test_live_weather_header_contrast_and_adaptability():
    """Kiểm tra độ tương phản và tính thích ứng giao diện Sáng/Tối của Tiêu đề Thời tiết thực tế."""
    at = AppTest.from_file(APP_FILE, default_timeout=25).run()
    assert at.session_state["app_mode"] == MODE_CITIZEN

    markdown_contents = [m.value for m in at.markdown]
    
    # 1. Tìm thấy khối live-weather-header-bar và tiêu đề thời tiết
    weather_headers = [m for m in markdown_contents if '<div class="live-weather-header-bar">' in m]
    assert len(weather_headers) >= 1, "Phải tìm thấy <div class=\"live-weather-header-bar\"> trong Mode 1"
    
    header_html = weather_headers[0]
    assert "📡 THỜI TIẾT THỰC TẾ TRỰC TUYẾN (TP. HỒ CHÍ MINH & THỦ ĐỨC)" in header_html
    assert "Open-Meteo Realtime API" in header_html
    
    # 2. Đảm bảo KHÔNG còn màu đen cứng #0F172A gây mất tương phản trên nền tối
    assert "color: #0F172A;" not in header_html, "Tiêu đề không được hardcode màu #0F172A gây chìm chữ trên theme tối"
    
    # 3. Phải sử dụng CSS variable var(--text-color, inherit) để chữ luôn tương phản cao
    assert "var(--text-color" in header_html, "Tiêu đề phải dùng biến CSS thích ứng với cả Dark mode và Light mode"
    assert "live-weather-title" in header_html
    assert "live-weather-source-badge" in header_html
    
    # 4. Kiểm tra sự hiện diện của app-footer-note thích ứng theme
    assert any("app-footer-note" in m for m in markdown_contents), "Footer note phải sử dụng class app-footer-note thích ứng"

def test_metric_risk_level_full_display_without_truncation():
    """Kiểm tra metric Mức độ rủi ro hiển thị đầy đủ (không bị cắt cụt dấu 3 chấm)."""
    at = AppTest.from_file(APP_FILE, default_timeout=25).run()

    # 1. Kiểm tra CSS chống truncate và cho phép wrap text trong metric
    css_content = [m.value for m in at.markdown if "<style>" in m.value][0]
    assert 'data-testid="stMetricValue"' in css_content
    assert "white-space: normal !important;" in css_content
    assert "text-overflow: unset !important;" in css_content

    # 2. Kiểm tra metric Mức độ rủi ro có mặt và giá trị đầy đủ tại Bước 5
    at.sidebar.radio(key="app_mode_radio").set_value(MODE_RESEARCH).run()
    assert len(at.exception) == 0
    at.button(key="top_step_5").click().run()
    assert len(at.exception) == 0
    risk_metrics = [m for m in at.metric if m.label == "Mức độ rủi ro"]
    assert len(risk_metrics) >= 1, "Phải có metric Mức độ rủi ro tại Bước 5"
    assert risk_metrics[0].value in ["THẤP / AN TOÀN", "TRUNG BÌNH", "CỰC KỲ CAO"]


def test_latency_indicator_contrast_and_adaptability():
    """Kiểm tra chỉ báo Độ trễ (Latency) đảm bảo độ tương phản cao và thích ứng Dark/Light Mode:
    - Sử dụng class .cyber-latency-label và .cyber-latency-val thay vì hardcode màu #0F172A / #475569.
    - CSS định nghĩa màu chữ và background badge nổi bật, tương thích cả 2 theme.
    - Áp dụng đồng bộ cho cả Mode 1 (Hero Center Telemetry Box) và Mode 2 (Bước 5 Live API Indicator).
    """
    at = AppTest.from_file(APP_FILE, default_timeout=25).run()
    assert at.session_state["app_mode"] == MODE_CITIZEN

    # 1. Kiểm tra CSS định nghĩa các class cyber-latency và telemetry dark/light mode
    css_content = [m.value for m in at.markdown if "<style>" in m.value][0]
    assert ".cyber-latency-label" in css_content
    assert ".cyber-latency-val" in css_content
    assert ".cyber-telemetry-subrow" in css_content
    assert '[data-theme="dark"] .cyber-latency-val' in css_content

    # 2. Kiểm tra Mode 1 (Citizen Live Portal): Khối Radar Center Telemetry Box
    markdown_contents_m1 = " ".join([m.value for m in at.markdown])
    assert "cyber-latency-label" in markdown_contents_m1
    assert "cyber-latency-val" in markdown_contents_m1
    assert "Độ trễ / Phản hồi (Latency):" in markdown_contents_m1
    # Không còn hardcoded style="color: #0F172A;" bên trong thẻ b latency của Mode 1
    assert '<b style="color: #0F172A;">' not in markdown_contents_m1

    # 3. Kiểm tra Mode 2 (Research Lab): Bước 5 Live API Indicator
    at.sidebar.radio(key="app_mode_radio").set_value(MODE_RESEARCH).run()
    at.button(key="top_step_5").click().run()
    markdown_contents_m2 = " ".join([m.value for m in at.markdown])
    assert "cyber-latency-label" in markdown_contents_m2
    assert "cyber-latency-val" in markdown_contents_m2
    assert "cyber-telemetry-sync-val" in markdown_contents_m2


def test_citizen_portal_interactive_gps_map_and_hotspots():
    """Kiểm tra bản đồ tương tác GPS thực tế (st.map) và 4 thẻ trạng thái điểm đen ngập úng trong Citizen Portal:
    - Sử dụng st.map (deck_gl_json_chart) thay vì hình ảnh SVG tĩnh thô sơ.
    - Hiển thị đầy đủ tọa độ UIT, điểm xuất phát động và 4 điểm đen ngập úng Thủ Đức.
    - Hiển thị 4 thẻ trạng thái chi tiết với huy hiệu cảnh báo (Báo động / Thông thoáng), độ ngập và tuyến né tránh.
    - Cập nhật điểm xuất phát mượt mà khi thay đổi selectbox lộ trình.
    """
    at = AppTest.from_file(APP_FILE, default_timeout=25).run()
    assert at.session_state["app_mode"] == MODE_CITIZEN
    assert len(at.exception) == 0

    # 1. Xác nhận sự hiện diện của bản đồ tương tác deck_gl_json_chart (st.map)
    maps = at.get("deck_gl_json_chart")
    assert len(maps) >= 1, "Citizen Portal phải chứa bản đồ GPS tương tác st.map (deck_gl_json_chart)"

    # 2. Kiểm tra tiêu đề bản đồ và thanh chú giải trực quan
    markdown_contents = " ".join([m.value for m in at.markdown])
    assert "Bản đồ" in markdown_contents and "4 điểm đen ngập úng xung quanh UIT" in markdown_contents
    assert "Trường ĐH CNTT (UIT)" in markdown_contents
    assert "Điểm xuất phát" in markdown_contents
    assert "4 Điểm đen Thủ Đức" in markdown_contents

    # 3. Kiểm tra 4 thẻ trạng thái điểm đen ngập úng
    assert "hotspot-compact-item" in markdown_contents
    assert "Tô Ngọc Vân" in markdown_contents
    assert "Chân cầu Bình Triệu" in markdown_contents
    assert "Dốc Võ Văn Ngân" in markdown_contents
    assert "Đặng Thị Rành" in markdown_contents
    assert ("Lưu thông:" in markdown_contents or "Né tránh:" in markdown_contents)

    # 4. Kiểm tra cập nhật điểm xuất phát động trên bản đồ khi chọn lộ trình
    origin_select = at.selectbox(key="route_origin_select")
    assert origin_select is not None
    origin_select.select("KTX Khu B (ĐHQG)").run()
    assert len(at.exception) == 0
    assert at.session_state["route_origin_select"] == "KTX Khu B (ĐHQG)"
    assert len(at.get("deck_gl_json_chart")) >= 1


def test_scada_top_header_title():
    """Kiểm tra thanh tiêu đề đỉnh trang #scada-top-header-title:
    - Mode 1: Hiển thị chính xác 'Cổng Giám Sát Ngập Cục Bộ Khu Vực UIT & Thủ Đức (UIT & Thu Duc Flood Portal)' kế bên nút expand sidebar.
    - Mode 2: Hiển thị 'Hệ Thống Dự Báo Nguy Cơ Mưa Ngập Cục Bộ Khu Vực UIT & Thủ Đức (Research Lab)'.
    - CSS và Watchdog JS: Đảm bảo có CSS #scada-top-header-title và watchdog updateTopHeaderTitle().
    """
    # 1. Kiểm tra tồn tại trong file mã nguồn
    with open(APP_FILE, "r", encoding="utf-8") as f:
        src = f.read()
    assert "#scada-top-header-title" in src
    assert "updateTopHeaderTitle" in src
    assert "position: relative !important;" in src
    assert "Cổng Giám Sát Ngập Cục Bộ Khu Vực UIT & Thủ Đức (UIT & Thu Duc Flood Portal)" in src

    # 2. Khởi chạy AppTest ở Mode 1 (Citizen Live Portal)
    at = AppTest.from_file(APP_FILE, default_timeout=25).run()
    assert at.session_state["app_mode"] == MODE_CITIZEN
    assert len(at.exception) == 0

    markdown_contents_m1 = " ".join([m.value for m in at.markdown])
    assert "id=\"scada-top-header-title\"" in markdown_contents_m1 or "id='scada-top-header-title'" in markdown_contents_m1
    assert "Cổng Giám Sát Ngập Cục Bộ Khu Vực UIT & Thủ Đức" in markdown_contents_m1
    assert "(UIT & Thu Duc Flood Portal)" in markdown_contents_m1
    assert "PORTAL LIVE" in markdown_contents_m1

    # 3. Chuyển sang Mode 2 (Research Lab) và kiểm tra thanh tiêu đề cập nhật tương ứng
    at.sidebar.radio(key="app_mode_radio").set_value(MODE_RESEARCH).run()
    assert len(at.exception) == 0
    assert at.session_state["app_mode"] == MODE_RESEARCH

    markdown_contents_m2 = " ".join([m.value for m in at.markdown])
    assert "id=\"scada-top-header-title\"" in markdown_contents_m2 or "id='scada-top-header-title'" in markdown_contents_m2
    assert "Hệ Thống Dự Báo Nguy Cơ Mưa Ngập Cục Bộ Khu Vực UIT & Thủ Đức" in markdown_contents_m2
    assert "(Research Lab)" in markdown_contents_m2
    assert "KDD LAB" in markdown_contents_m2
