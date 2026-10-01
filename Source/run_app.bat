@echo off
chcp 65001 > nul
cls

echo ======================================================================
echo  DO AN MON HOC IE403: KHAI THAC DU LIEU VA TRUYEN THONG XA HOI
echo  HE THONG DU BAO NGUY CO MUA NGAP CUC BO KHU VUC UIT & THU DUC (KDD)
echo  Nhom: 12 - Sinh vien: NGUYEN DUY NHIEM -  (IE403.P11)
echo  Giang vien huong dan: ThS. Mai Xuan Hung - Truong DH CNTT (UIT - DHQG-HCM)
echo  Ban quyen (C) 2026 Nguyen Duy Nhiem. Bao luu moi quyen.
echo ======================================================================
echo.

:: 1. Chuyen den thu muc chua file script nay
cd /d "%~dp0"

:: 2. Tu dong vao thu muc Source neu dang o thu muc goc
if exist "Source" cd "Source"

:: 3. Kiem tra xem co file ung dung streamlit_app.py khong
if exist "app\streamlit_app.py" goto APP_FOUND
echo ======================================================================
echo  [LOI] Khong tim thay tep app\streamlit_app.py!
echo  Vui long dam bao ban dang mo dung thu muc do an.
echo ======================================================================
pause
exit /b 1

:APP_FOUND
:: 4. Phat hien trinh thuc thi Python
set PYTHON_CMD=
py -3 -c "import sys; assert sys.version_info >= (3, 8)" >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=py -3
    goto PYTHON_READY
)
python -c "import sys; assert sys.version_info >= (3, 8)" >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto PYTHON_READY
)
python3 -c "import sys; assert sys.version_info >= (3, 8)" >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3
    goto PYTHON_READY
)

:: Neu khong tim thay Python
echo ======================================================================
echo  [CANH BAO] CHUA TIM THAY PYTHON 3 TREN MAY TINH CUA THAY / CO!
echo ======================================================================
echo  De chay chuong trinh demo, may tinh can cai dat Python 3.10 tro len.
echo.
echo  HUONG DAN CAI DAT NHANH:
echo  1. He thong dang tu dong mo trang tai Python tu https://www.python.org/
echo  2. Khi cai dat, LUU Y QUAN TRONG NHAT:
echo     Hay danh dau tich vao o:
echo        [x] "Add python.exe to PATH"  (o duoi cung cua so cai dat)
echo  3. Sau khi cai dat xong, hay chay lai file run_app.bat nay!
echo ======================================================================
echo.
start https://www.python.org/downloads/
pause
exit /b 1

:PYTHON_READY
echo [1/3] Kiem tra moi truong Python...
%PYTHON_CMD% -c "import sys; print(f'      Da tim thay: Python {sys.version.split[0]}')"

:: 5. Tu dong tao moi truong ao .venv neu chua co
if exist ".venv" goto VENV_EXISTS
echo.
echo [1/3] Dang tu dong khoi tao moi truong ao .venv de cach ly thu vien...
echo       Viec nay giup cach ly thu vien, khong gay anh huong may tinh cua Thay/Co.
%PYTHON_CMD% -m venv .venv
if %errorlevel% neq 0 (
    echo [Luu y] Khong khoi tao duoc .venv, se su dung truc tiep Python he thong.
    set PYTHON_EXEC=%PYTHON_CMD%
    goto CHECK_DEPS
)

:VENV_EXISTS
if exist ".venv\Scripts\activate.bat" (
    echo [1/3] Kich hoat moi truong ao .venv...
    call ".venv\Scripts\activate.bat"
    set PYTHON_EXEC=python
) else (
    set PYTHON_EXEC=%PYTHON_CMD%
)

:CHECK_DEPS
:: 6. Kiem tra thu vien phu thuoc
echo [2/3] Kiem tra cac thu vien can thiet (Streamlit, Pandas, Scikit-learn, Joblib)...
%PYTHON_EXEC% -c "import streamlit, pandas, sklearn, joblib, matplotlib" >nul 2>nul
if %errorlevel% equ 0 goto DEPS_READY

echo.
echo [THONG BAO] Phat hien thieu thu vien hoac lan dau khoi chay!
echo             Dang tu dong tai va cai dat cac goi tu requirements.txt...
echo             (Qua trinh nay mat khoang 1-2 phut tuy toc do mang, vui long doi...)
echo.
%PYTHON_EXEC% -m pip install - upgrade pip - quiet
%PYTHON_EXEC% -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ======================================================================
    echo  [LOI] Khong the tu dong cai dat thu vien tu PyPI.
    echo  Vui long kiem tra ket noi mang Internet hoac chay thu cong:
    echo      pip install -r requirements.txt
    echo ======================================================================
    pause
    exit /b 1
)
echo [OK] Da cai dat thanh cong cac thu vien can thiet!

:DEPS_READY
echo [OK] Cac thu vien da duoc cai dat day du!

:: 7. Kiem tra cong mang (Port) de tranh xung dot
set APP_PORT=8501
for /f %%p in ('%PYTHON_EXEC% -c "import socket; p = next((x for x in (8501, 8502, 8503, 8504) if socket.socket.connect_ex(('127.0.0.1', x)) != 0), 8501); print(p)"') do set APP_PORT=%%p
if not "%APP_PORT%"=="8501" (
    echo.
    echo [THONG BAO] Cong 8501 dang ban, tu dong chuyen sang cong %APP_PORT%...
)

:: 8. Khoi chay Web App
echo.
echo ======================================================================
echo  [3/3] Dang khoi chay He Thong Giam Sat va Du Bao Mua Ngap UIT tai:
echo        http://localhost:%APP_PORT%
echo.
echo  Trinh duyet Web (Chrome/Edge/Coccoc) se tu dong mo ung dung.
echo  (Nhan to hop phim Ctrl + C trong cua so nay neu muon dung ung dung)
echo ======================================================================
echo.

%PYTHON_EXEC% -m streamlit run app/streamlit_app.py - server.port %APP_PORT% - server.headless false

echo.
echo Ung dung da dong.
pause
