@echo off
echo Starting SDF processing...
set PYTHONPATH=Y:\_Utilities\AssetPipeline
call "%~dp0core\sdf_processor.exe" %*
echo Processing complete!
pause