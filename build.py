import os
import sys
import subprocess
import platform

def install_dependencies():
    print("Checking and installing build dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        sys.exit(1)

def build_windows():
    if platform.system() != "Windows":
        print("Error: build.py for Windows must be run on a Windows machine.")
        sys.exit(1)

    install_dependencies()

    print("\nStarting build process for Windows...")

    # Nuitka command
    command = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--enable-plugin=pyside6",
        "--windows-disable-console",
        "--include-data-files=styles.qss=styles.qss",
        "--output-dir=dist",
        "--output-filename=StreamLabsTikTokStreamKeyGenerator",
        "StreamLabsTikTokStreamKeyGenerator.py"
    ]

    try:
        print(f"Running: {' '.join(command)}")
        subprocess.run(command, check=True)
        print("\nBuild successful! The executable can be found in the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_windows()
