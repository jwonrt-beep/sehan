@echo off
chcp 65001 > nul
echo.
echo ====================================================
echo   파나소닉 용접로봇 재고관리 시스템
echo ====================================================
echo.

REM Python 설치 확인
python --version > nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo https://python.org 에서 Python 3.11 이상을 설치하세요.
    pause
    exit /b
)

REM Flask 설치 확인 및 자동 설치
python -c "import flask" > nul 2>&1
if errorlevel 1 (
    echo Flask를 설치합니다...
    pip install flask werkzeug
)

echo 서버를 시작합니다...
echo.
python app.py
pause
