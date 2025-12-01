from setuptools import setup, find_packages

import os

# Read version from __version__.py
with open(os.path.join("nanohubdashboard", "__version__.py")) as f:
    exec(f.read())

setup(
    name="nanohub-dashboards",
    version=__version__,
    description="Python client library for interacting with the nanoHUB Dashboard API",
    author="nanoHUB",
    author_email="support@nanohub.org",
    url="https://github.com/denphi/nanohub-dashboards",
    packages=find_packages(exclude=["examples", "examples.*"]),
    install_requires=[
        "requests",
        "plotly",
        "pandas",
        "nanohub-remote"
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords=["nanohub", "dashboard", "visualization", "plotly"],
)
