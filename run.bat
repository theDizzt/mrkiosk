@echo off
chcp 65001
title MR Kiosk Auto Launcher
cd /d "%~dp0"

echo ========================================================
echo  [SYSTEM] MR Kiosk 가이드라인 엔진 가동 프로토콜
echo ========================================================
echo.

:: 2단계: 파이썬 내부 모듈 참조 환경변수 등록 (팀원 설정 유지)
set PYTHONPATH=vision

:: 3단계: [★수정완료] 진짜 메인 엔진인 app_aruco_dual.py 구동 및 UDP 전송 옵션 세팅
echo   [2단계] 듀얼 아루코 포즈 최적화 및 가이드라인 엔진을 가동합니다...
"C:\Users\dhkim\miniconda3\python.exe" vision/app_aruco_dual.py --reference-id 769 --show --udp-host 192.168.200.106 --udp-port 5005

pause