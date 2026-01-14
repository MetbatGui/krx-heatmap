@echo off
echo 테마 히트맵 생성 중...
cd apps\theme_heatmap
uv run python main.py
cd ..\..
pause
