@echo off
cd /d %~dp0

echo Syncing dependencies...
uv sync

echo Running heatmap generation...
uv run theme_heatmap.py

pause
