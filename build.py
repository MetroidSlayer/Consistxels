import subprocess
import sys
from pathlib import Path
# import shutil

BASE_DIR = Path(__file__).parent.resolve()

if __name__ == "__main__":
    subprocess.run([
        sys.executable, "-m", "PyInstaller",
        str(BASE_DIR / "Consistxels.spec")
    ], check=True)

    # shutil.move(os.path.join(BASE_DIR, "resources"), os.path.join(BASE_DIR, "dist", "Consistxels"))
    # shutil.copy2(os.path.join(BASE_DIR, "resources"), os.path.join(BASE_DIR, "dist", "Consistxels"))
    # At some point, need to automate copying resources. Doing it manually for now
