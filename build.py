import os
import sys
import subprocess
import platform

def install_requirements():
    print("Installing build-time dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "nuitka", "pyside6", "requests", "packaging"])

def build():
    if platform.system() != "Windows":
        print("Build script is primarily for Windows.")
        # But we can still try to run Nuitka if desired

    print("Starting build with Nuitka...")

    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--plugin-enable=pyside6",
        "--windows-disable-console",
        "--include-data-file=styles.qss=styles.qss",
        "--windows-icon-from-ico=logo.ico", # If exists, otherwise remove
        "--output-dir=dist",
        "StreamLabsTikTokStreamKeyGenerator.py"
    ]

    # Check if logo.ico exists
    if not os.path.exists("logo.ico"):
        cmd = [c for c in cmd if "--windows-icon-from-ico" not in c]

    try:
        subprocess.check_call(cmd)
        print("Build successful! Check the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")

if __name__ == "__main__":
    install_requirements()
    build()
