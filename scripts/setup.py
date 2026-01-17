"""
Project Khufra AI - Setup Script
Automated setup for the trading bot.
"""

import sys
import subprocess
from pathlib import Path
import shutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def print_header(message: str):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {message}")
    print("=" * 60 + "\n")


def print_step(step: str):
    """Print step message."""
    print(f"📌 {step}")


def print_success(message: str):
    """Print success message."""
    print(f"✅ {message}\n")


def print_error(message: str):
    """Print error message."""
    print(f"❌ {message}\n")


def check_python_version():
    """Check if Python version is 3.11+."""
    print_step("Checking Python version...")

    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print_error(f"Python 3.11+ required. You have Python {version.major}.{version.minor}")
        return False

    print_success(f"Python {version.major}.{version.minor}.{version.micro} - OK")
    return True


def check_virtual_environment():
    """Check if running in virtual environment."""
    print_step("Checking virtual environment...")

    if sys.prefix == sys.base_prefix:
        print("⚠️  Not running in a virtual environment")
        print("   It's recommended to use a virtual environment")
        create = input("   Create virtual environment now? (y/n): ").lower()

        if create == 'y':
            print("   Creating virtual environment...")
            try:
                subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
                print_success("Virtual environment created! Please activate it and run this script again.")
                print("   Windows: venv\\Scripts\\activate")
                print("   Linux/Mac: source venv/bin/activate")
                sys.exit(0)
            except Exception as e:
                print_error(f"Failed to create virtual environment: {e}")
                return False
        else:
            print("   Proceeding without virtual environment...\n")
    else:
        print_success("Virtual environment active")

    return True


def install_dependencies():
    """Install required Python packages."""
    print_step("Installing dependencies...")

    requirements_file = Path(__file__).parent.parent / "requirements.txt"

    if not requirements_file.exists():
        print_error("requirements.txt not found!")
        return False

    try:
        print("   This may take a few minutes...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            check=True
        )
        print_success("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False


def create_env_file():
    """Create .env file from .env.example."""
    print_step("Setting up environment file...")

    project_root = Path(__file__).parent.parent
    env_example = project_root / ".env.example"
    env_file = project_root / ".env"

    if env_file.exists():
        print("   .env file already exists")
        overwrite = input("   Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            print("   Keeping existing .env file\n")
            return True

    if not env_example.exists():
        print_error(".env.example not found!")
        return False

    try:
        shutil.copy(env_example, env_file)
        print_success(".env file created from template")
        print("⚠️  IMPORTANT: Edit .env file and add your API keys!\n")
        return True
    except Exception as e:
        print_error(f"Failed to create .env file: {e}")
        return False


def create_directories():
    """Create necessary directories."""
    print_step("Creating directories...")

    project_root = Path(__file__).parent.parent
    directories = [
        project_root / "data",
        project_root / "data" / "logs",
    ]

    try:
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"   Created: {directory.name}/")

        print_success("Directories created")
        return True
    except Exception as e:
        print_error(f"Failed to create directories: {e}")
        return False


def initialize_database():
    """Initialize the database."""
    print_step("Initializing database...")

    try:
        from config.settings import settings
        from src.database.connection import DatabaseManager
        from src.database.models import Base
        import asyncio

        async def setup_db():
            db_manager = DatabaseManager(settings.DATABASE_URL)
            await db_manager.connect()
            print("   Database tables created successfully")
            await db_manager.disconnect()

        asyncio.run(setup_db())
        print_success("Database initialized")
        return True

    except Exception as e:
        print_error(f"Failed to initialize database: {e}")
        return False


def run_tests():
    """Run basic tests to verify setup."""
    print_step("Running basic tests...")

    try:
        # Test imports
        from config.settings import settings
        from src.utils.logger import setup_logger
        from src.database.models import Trade

        print("   ✓ Configuration module")
        print("   ✓ Logger module")
        print("   ✓ Database models")

        print_success("Basic tests passed")
        return True

    except Exception as e:
        print_error(f"Tests failed: {e}")
        return False


def main():
    """Main setup function."""
    print_header("PROJECT KHUFRA AI - SETUP WIZARD")

    print("This script will set up your Khufra AI trading bot environment.\n")
    print("What will be done:")
    print("  1. Check Python version")
    print("  2. Check/create virtual environment")
    print("  3. Install dependencies")
    print("  4. Create .env file")
    print("  5. Create necessary directories")
    print("  6. Initialize database")
    print("  7. Run basic tests")
    print()

    proceed = input("Proceed with setup? (y/n): ").lower()
    if proceed != 'y':
        print("\nSetup cancelled.")
        sys.exit(0)

    # Run setup steps
    steps = [
        ("Python Version Check", check_python_version),
        ("Virtual Environment", check_virtual_environment),
        ("Dependencies", install_dependencies),
        ("Environment File", create_env_file),
        ("Directories", create_directories),
        ("Database", initialize_database),
        ("Tests", run_tests),
    ]

    failed_steps = []

    for step_name, step_func in steps:
        if not step_func():
            failed_steps.append(step_name)
            print(f"⚠️  {step_name} failed, but continuing...\n")

    # Summary
    print_header("SETUP COMPLETE")

    if failed_steps:
        print("⚠️  Some steps failed:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\nPlease fix these issues before running the bot.\n")
    else:
        print("✅ All setup steps completed successfully!\n")

        print("NEXT STEPS:")
        print("  1. Edit .env file and add your API keys")
        print("  2. Review config/strategies.json (waiting for Anjing's strategies)")
        print("  3. Test the bot: python main.py")
        print("  4. Start trading (paper mode first!)")
        print()

    print("For detailed documentation, see: docs/setup_guide.md")
    print()


if __name__ == "__main__":
    main()
