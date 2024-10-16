# livekit_api/setup.py

import os
import pathlib
from typing import Any, Dict

import setuptools  # type: ignore

here = pathlib.Path(__file__).parent.resolve()
about: Dict[Any, Any] = {}
with open(os.path.join(here, "livekit", "api", "version.py"), "r") as f:
    exec(f.read(), about)


setuptools.setup(
    name="livekit_api",  # Updated package name
    version=about["__version__"],
    description="Python Server API for LiveKit",
    long_description=(here / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/livekit/python-sdks",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
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
    python_requires=">=3.9.0",
    install_requires=[
        "pyjwt>=2.0.0",
        "aiohttp>=3.9.0",
        "protobuf>=3",
        "types-protobuf>=4,<5",
        "livekit_protocol>=0.6.0,<1",  # Updated dependency
    ],
    package_data={
        "livekit.api": ["py.typed", "*.pyi", "**/*.pyi"],
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
