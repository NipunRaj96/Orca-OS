"""
Setup script for Orca OS.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="orca-os",
    version="0.1.0",
    author="Orca OS Team",
    author_email="team@orca-os.dev",
    description="AI-powered operating system wrapper for Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/orca-os/orca",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "orca=orca.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "orca": ["config/*.yaml"],
    },
)
