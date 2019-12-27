#!/usr/bin/env python
# noqa
# pylint: skip-file
"""The setup script."""
from setuptools import setup

with open("requirements.txt", "r") as filein:
    requirements = filein.readlines()

with open("requirements-dev.txt", "r") as filein:
    test_requirements = filein.readlines()

with open("version.txt", "r") as filein:
    version = filein.read()

with open("README.md", "r") as filein:
    readme = filein.read()


setup_requirements: list = [
    "setuptools >= 41.0.0",
    # python3 specifically requires wheel 0.26
    'wheel; python_version < "3"',
    'wheel >= 0.26; python_version >= "3"',
]

setup(
    author="eterna2",
    author_email="eterna2@hotmail.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="Productivity functions for common but painful pyspark tasks.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/e2fyi/pyspark-utils",
    include_package_data=True,
    package_data={
        "": [
            "version.txt",
            "requirements.txt",
            "requirements-dev.txt",
            "test.py",
            "README.md",
        ]
    },
    keywords="util pyspark",
    name="e2fyi-pyspark",
    packages=["e2fyi.pyspark"],
    setup_requires=setup_requirements,
    python_requires=">=3.6",
    install_requires=requirements,
    test_suite="e2fyi",
    tests_require=test_requirements,
    version=version,
    zip_safe=False,
)
