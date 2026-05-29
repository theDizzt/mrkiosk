@echo off
chcp 65001
title MR Kiosk Auto Launcher
cd /d "%~dp0"

echo ========================================================
echo  [SYSTEM] MR Kiosk 가이드라인 엔진 가동 프로토콜
echo ========================================================
echo.

:: 1단계: 님의 3.12 파이썬 엔진을 정확한 절대 주소로 강제 지정하여 마커 생성
echo  [1단계] 아루코 마커 이미지 에셋을 일괄 생성 중입니다...
"C:\Users\dhkim\miniconda3\python.exe" vision/make_markers.py
echo.

:: 2단계: 파이썬 내부 모듈 참조 환경변수 등록
set PYTHONPATH=vision

:: 3단계: 동일한 파이썬 엔진 주소로 메인 웹캠 포즈/TTS 시스템 강제 구동
echo [2단계] OpenCV 포즈 최적화 및 TTS 엔진을 가동합니다...
"C:\Users\dhkim\miniconda3\python.exe" vision/app_pose.py

pause