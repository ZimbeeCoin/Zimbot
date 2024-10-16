# livekit_protocol/setup.py

import os
import pathlib
from typing import Any, Dict

import setuptools  # type: ignore

here = pathlib.Path(__file__).parent.resolve()
about: Dict[Any, Any] = {}
with open(os.path.join(here, "livekit", "protocol", "version.py"), "r") as f:
    exec(f.read(), about)


setuptools.setup(
    name="livekit_protocol",  # Updated package name
    version=about["__version__"],
    description="Python protocol stubs for LiveKit",
    long_description="Python protocol stubs for LiveKit",
    long_description_content_type="text/markdown",
    url="https://github.com/livekit/python-sdks",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords=["webrtc", "realtime", "audio", "video", "livekit"],
    license="Apache-2.0",
    packages=setuptools.find_namespace_packages(include=["livekit.*"]),
    python_requires=">=3.7.0",
    install_requires=[
        "protobuf>=3",
        "types-protobuf>=4,<5",
    ],
    package_data={
        "livekit.protocol": ["*.pyi", "**/*.pyi", "py.typed"],
    },
    project_urls={
        "Documentation": "https://docs.livekit.io",
        "Website": "https://www.zimbeecoin.com/",
        "Source": "https://github.com/livekit/python-sdks/",
    },
    author="Michael Smith",
    author_email="michaelsmithking1229@gmail.com",
    maintainer="Michael Smith",
    maintainer_email="michaelsmithking1229@gmail.com",
)
