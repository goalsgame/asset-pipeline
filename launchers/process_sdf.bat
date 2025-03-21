@echo off
echo Starting SDF processing...
set PYTHONPATH=Y:\_Utilities\AssetPipeline
call "%~dp0core\sdf_processor.exe" --config configs/sdf_processor.cfg %*
echo Processing complete!
pause