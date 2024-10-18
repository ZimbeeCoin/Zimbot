import os
import pathlib
from sysconfig import get_platform
from typing import Any, Dict

import setuptools
from setuptools import find_packages
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

# Read the current directory
here = pathlib.Path(__file__).parent.resolve()

# Load the version from livekit/rtc/version.py
about: Dict[Any, Any] = {}
with open(os.path.join(here, "livekit", "rtc", "version.py"), "r") as f:
    exec(f.read(), about)

# Custom bdist_wheel to handle platform-specific packaging
class bdist_wheel(_bdist_wheel):
    def finalize_options(self):
        self.plat_name = get_platform()  # force a platform tag
        _bdist_wheel.finalize_options(self)

# Package setup configuration
setuptools.setup(
    name="livekit_rtc",  # Package name
    version=about.get("__version__", "0.1.0"),  # Version from version.py, default to 0.1.0 if missing
    description="Python Real-time SDK for LiveKit and RTC integration for ZIMBOT",
    long_description=(here / "README.md").read_text(encoding="utf-8"),  # Ensure README.md exists for this
    long_description_content_type="text/markdown",  # Readme format
    url="https://github.com/ZimbeeCoin/Zimbot",  # Update URL to your GitHub repo
    author="Tatelyn Jenner",
    author_email="tatelynjenner@gmail.com",
    maintainer="Michael Smith",
    maintainer_email="michaelsmithking1229@gmail.com",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords=["webrtc", "realtime", "audio", "video", "livekit", "ZIMBOT"],
    license="Apache-2.0",
    packages=find_packages(),  # Automatically find all packages in the directory
    python_requires=">=3.9.0",  # Specify required Python versions
    install_requires=[
        "protobuf>=3",  # Dependencies for LiveKit RTC
        "types-protobuf>=3",
    ],
    package_data={  # Include additional data files required for this package
        "livekit.rtc": ["_proto/*.py", "py.typed", "*.pyi", "**/*.pyi"],
        "livekit.rtc.resources": ["*.so", "*.dylib", "*.dll", "LICENSE.md", "*.h"],
    },
    project_urls={  # Project-related URLs
        "Documentation": "https://docs.livekit.io",
        "Website": "https://www.zimbeecoin.com/",
        "Source": "https://github.com/livekit/python-sdks/",
    },
    cmdclass={  # Custom wheel configuration
        "bdist_wheel": bdist_wheel,
    },
)
