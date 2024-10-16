# livekit_rtc/setup.py

import os
import pathlib
from sysconfig import get_platform
from typing import Any, Dict

import setuptools  # type: ignore
import setuptools.command.build_py  # type: ignore
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel  # type: ignore

here = pathlib.Path(__file__).parent.resolve()
about: Dict[Any, Any] = {}
with open(os.path.join(here, "livekit", "rtc", "version.py"), "r") as f:
    exec(f.read(), about)


class bdist_wheel(_bdist_wheel):
    def finalize_options(self):
        self.plat_name = get_platform()  # force a platform tag
        _bdist_wheel.finalize_options(self)


setuptools.setup(
    name="livekit_rtc",  # Updated package name
    version=about["__version__"],
    description="Python Real-time SDK for LiveKit",
    long_description=(here / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/livekit/python-sdks",
    cmdclass={
        "bdist_wheel": bdist_wheel,
    },
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords=["webrtc", "realtime", "audio", "video", "livekit"],
    license="Apache-2.0",
    packages=setuptools.find_namespace_packages(include=["livekit.*"]),
    python_requires=">=3.9.0",
    install_requires=[
        "protobuf>=3",
        "types-protobuf>=3",
    ],
    package_data={
        "livekit.rtc": ["_proto/*.py", "py.typed", "*.pyi", "**/*.pyi"],
        "livekit.rtc.resources": ["*.so", "*.dylib", "*.dll", "LICENSE.md", "*.h"],
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
