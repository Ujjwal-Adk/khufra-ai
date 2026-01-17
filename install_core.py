"""
Quick installer for core dependencies
Run this if setup.py fails
"""

import subprocess
import sys

def install_package(package):
    """Install a single package."""
    try:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}\n")
        return False

def main():
    print("=" * 60)
    print("  PROJECT KHUFRA AI - CORE DEPENDENCIES INSTALLER")
    print("=" * 60)
    print()

    # Core packages that MUST work
    core_packages = [
        "python-dotenv",
        "pydantic",
        "pydantic-settings",
        "sqlalchemy",
        "colorlog",
        "requests",
        "aiohttp",
        "tenacity",
        "python-dateutil",
        "pytz",
    ]

    print("Installing core packages (this may take 2-3 minutes)...\n")

    successful = 0
    failed = 0

    for package in core_packages:
        if install_package(package):
            successful += 1
        else:
            failed += 1

    print("=" * 60)
    print("  INSTALLATION SUMMARY")
    print("=" * 60)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print()

    if failed == 0:
        print("🎉 All core packages installed successfully!")
        print()
        print("Next steps:")
        print("  1. Copy .env.example to .env")
        print("  2. Add your API keys to .env")
        print("  3. Run: python main.py")
        print()
    else:
        print("⚠️  Some packages failed to install.")
        print("Try installing them manually:")
        print()
        for package in core_packages:
            print(f"  pip install {package}")
        print()

    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
