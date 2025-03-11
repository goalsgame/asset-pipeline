@echo off
echo Starting SDF processing...
set PYTHONPATH=Y:\_Utilities\AssetPipeline
call "%~dp0.venv\Scripts\python.exe" "%~dp0processors\sdf\run.py" %*
echo Processing complete!
pause