@echo off
chcp 65001
title MR Kiosk Auto Launcher
cd /d "%~dp0"

echo ========================================================
echo  [SYSTEM] Pose 최적화 엔진을 가동합니다.
echo ========================================================
echo.

:: 파이썬이 vision 폴더 안의 모듈들을 인식하도록 설정
set PYTHONPATH=vision

:: 파이썬 3.12 엔진으로 팀원의 app_pose.py 강제 실행
C:\Users\dhkim\AppData\Local\Programs\Python\Python312\python.exe vision/app_pose.py

pause