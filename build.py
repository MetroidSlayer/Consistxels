import os
import sys
import subprocess
import shutil

from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()

# Builds Consistxels.exe
if __name__ == "__main__":
    # Args for subprocess / PyInstaller
    args = [
        sys.executable, "-m", "PyInstaller",
        str(BASE_DIR / "Consistxels.spec"),
    ]

    # Add your own upx download to this directory. At some point, I could make it a command line arg, but ehh
    # Download upx: https://upx.github.io/
    upx_directory = os.path.join(BASE_DIR, 'upx')
    if os.path.exists(upx_directory):
        args.append(f"--upx-dir='{upx_directory}'")

    # Run PyInstaller and build Consistxels.exe
    subprocess.run(args, check=True)

    # Copy resources folder into dist/Consistxels
    shutil.copytree(os.path.join(BASE_DIR, "resources"), os.path.join(BASE_DIR, "dist", "Consistxels", "resources"))
    print("./resources copied successfully")
