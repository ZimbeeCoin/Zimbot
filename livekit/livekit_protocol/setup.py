import os
import pathlib
from typing import Any, Dict

import setuptools
from setuptools import find_packages

# Load current directory
here = pathlib.Path(__file__).parent.resolve()

# Load the version from livekit/protocol/version.py
about: Dict[Any, Any] = {}
with open(os.path.join(here, "livekit", "protocol", "version.py"), "r") as f:
    exec(f.read(), about)

# Setup configuration for livekit_protocol
setuptools.setup(
    name="livekit_protocol",  # Package name
    version=about.get("__version__", "0.1.0"),  # Version from version.py, default to 0.1.0 if missing
    description="LiveKit Protocol integration for ZIMBOT",  # Updated description
    long_description="Python protocol stubs for LiveKit",
    long_description_content_type="text/markdown",
    url="https://github.com/ZimbeeCoin/Zimbot",  # Updated repository URL
    author="Tatelyn Jenner",
    author_email="tatelynjenner@gmail.com",
    maintainer="Michael Smith",
    maintainer_email="michaelsmithking1229@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords=["webrtc", "realtime", "audio", "video", "livekit"],
    license="Apache-2.0",
    packages=find_packages(),  # Automatically find packages in the directory
    python_requires=">=3.7",
    install_requires=[
        "protobuf>=3",
        "types-protobuf>=4,<5",
    ],
    package_data={  # Include additional files
        "livekit.protocol": ["*.pyi", "**/*.pyi", "py.typed"],
    },
    project_urls={
        "Documentation": "https://docs.livekit.io",
        "Website": "https://www.zimbeecoin.com/",
        "Source": "https://github.com/livekit/python-sdks/",
    },
)
