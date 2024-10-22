# upgrade_packages.py

import subprocess
import sys
from importlib.metadata import distribution, PackageNotFoundError

def upgrade_package(package: str):
    """Upgrade a single package to the latest stable version."""
    try:
        print(f"Upgrading {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])
        print(f"{package} upgraded successfully!\n")
    except subprocess.CalledProcessError as e:
        print(f"Failed to upgrade {package}. Error: {e}\n")

def install_specific_version(package: str, version: str):
    """Install a specific version of a package."""
    try:
        print(f"Installing {package}=={version} to satisfy dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", f"{package}=={version}"])
        print(f"{package}=={version} installed successfully!\n")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package}=={version}. Error: {e}\n")

def remove_package(package: str):
    """Remove a specific package if it's installed."""
    try:
        distribution(package)
        print(f"Removing outdated package {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", package])
        print(f"{package} removed successfully!\n")
    except PackageNotFoundError:
        print(f"{package} is not installed. Skipping removal...\n")
    except subprocess.CalledProcessError as e:
        print(f"Failed to remove {package}. Error: {e}\n")

def main():
    # List of packages to upgrade, excluding those with strict dependencies and PyJWT
    packages_to_upgrade = [
        "APScheduler",
        "Deprecated",
        "Mako",
        "MarkupSafe",
        "SQLAlchemy",
        "aiohappyeyeballs",
        "aiohttp",
        "aiosignal",
        "alembic",
        "alpha_vantage",
        "annotated-types",
        "anyio",
        "asgiref",
        "async-timeout",
        "attrs",
        "autocommand",
        "backports.tarfile",
        "bcrypt",
        "blinker",
        "cachetools",
        "certifi",
        "cffi",
        "charset-normalizer",
        "click",
        "colorama",
        "cryptography",
        "distro",
        "ecdsa",
        "exceptiongroup",
        "fastapi",
        "Flask",
        "flask-swagger-ui",
        "frozenlist",
        "greenlet",
        "grpcio",
        "grpcio-tools",
        "h11",
        "httpcore",
        "httpx",
        "idna",
        "iniconfig",
        "itsdangerous",
        "jaraco.collections",
        "jaraco.context",
        "jaraco.functools",
        "jaraco.text",
        "Jinja2",
        "jiter",
        "limits",
        "livekit",
        "loguru",
        "Mako",
        "MarkupSafe",
        "more-itertools",
        "multidict",
        "mypy",
        "mypy-extensions",
        "openai",
        "packaging",
        "passlib",
        "platformdirs",
        "pluggy",
        "propcache",
        "protobuf",
        "py",
        "pyasn1",
        "pycoingecko",
        "pycparser",
        "pydantic",
        "pytest",
        "python-dotenv",
        "python-telegram-bot",
        "pytz",
        "redis",
        "requests",
        "rsa",
        "sentry-sdk",
        "six",
        "slowapi",
        "sniffio",
        "starlette",
        "stripe",
        "tomli",
        "tornado",
        "tqdm",
        "typeguard",
        "types-protobuf",
        "typing_extensions",
        "tzdata",
        "tzlocal",
        "urllib3",
        "uvicorn",
        "Werkzeug",
        "wrapt",
        "yarl",
        "zipp",
    ]

    # Packages with strict version requirements
    strict_packages = {
        "pydantic-core": "2.23.4",
        "starlette": "0.40.0",
        "protobuf": "5.29.0",  # Latest stable version
    }

    # Packages to remove (e.g., old 'jwt' package if present)
    packages_to_remove = [
        "jwt",  # Old JWT package to be removed
    ]

    # Upgrade general packages
    for package in packages_to_upgrade:
        # Skip strict packages
        if package in strict_packages:
            continue
        try:
            # Check if the package is installed
            distribution(package)
            upgrade_package(package)
        except PackageNotFoundError:
            print(f"{package} not found. Installing latest version...")
            upgrade_package(package)

    # Handle strict packages by installing specific versions
    for package, version in strict_packages.items():
        install_specific_version(package, version)

    # Remove outdated packages
    for package in packages_to_remove:
        remove_package(package)

if __name__ == "__main__":
    main()
