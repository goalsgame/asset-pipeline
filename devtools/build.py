from pathlib import Path
import shutil
import subprocess

# Define paths
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
DIST_DIR: Path = PROJECT_ROOT / "dist"
CORE_DIR: Path = DIST_DIR / "core"

# Clean build directory
if DIST_DIR.exists():
    shutil.rmtree(DIST_DIR)
DIST_DIR.mkdir(parents=True, exist_ok=True)
CORE_DIR.mkdir(parents=True, exist_ok=True)

# Build executables
BUILD_TARGETS = [
    ("asset_pipeline/processors/sdf/__main__.py", "sdf_processor"),
]

for script, exe_name in BUILD_TARGETS:
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", exe_name,
        "--distpath", str(CORE_DIR),  # Ensure CORE_DIR is passed as a string
        str(PROJECT_ROOT / script)    # Resolve the script path as string
    ]
    subprocess.run(cmd, check=True)

# Copy additional files
launchers_dir = PROJECT_ROOT / "launchers"
shutil.copytree(launchers_dir, DIST_DIR, dirs_exist_ok=True)

print(f"Build complete! Check the '{DIST_DIR}' directory.")