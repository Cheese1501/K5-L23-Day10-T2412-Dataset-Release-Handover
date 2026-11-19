@echo off
rem Nhap dup de mo ban lam viec review tren Windows. Them tham so neu can, vi du:
rem   lab\MO_LAB_WINDOWS.cmd --run runs\de_an_work --delivery delivery
cd /d "%~dp0.."
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
if "%~1"=="" (
  py lab\review_server.py --run runs\r2412007 --port 8765 --open
) else (
  py lab\review_server.py --port 8765 --open %*
)
pause
