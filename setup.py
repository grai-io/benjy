import os
from pathlib import Path

from setuptools import find_packages, setup

source_root = Path(".")

with (source_root / "README.md").open(encoding="utf-8") as f:
    long_description = f.read()

# Read the requirements
with (source_root / "requirements.txt").open(encoding="utf8") as f:
    requirements = f.readlines()

__version__ = None
with (source_root / "src/benjy/version.py").open(encoding="utf8") as f:
    exec(f.read())

setup(
    name="benjy",
    version=__version__,
    url="https://github.com/grai-io/arthur",
    description="Benjy",
    author="Grai.io",
    author_email="ian@grai.io",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=requirements,
    include_package_data=True,
    # extras_require=extras_requires,
    # tests_require=test_requirements,
    python_requires=">=3.6",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "benjy = benjy.cli:cli",
        ],
    },
)
