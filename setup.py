#!/usr/bin/env python
from setuptools import setup

setup(
    name="target-sas7bdat",
    version="0.1.0",
    description="Singer.io target for extracting data",
    author="Stitch",
    url="http://singer.io",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["target-sas7bdat"],
    install_requires=[
        "singer-python>=5.0.12",
        'jsonschema==2.6.0',
        "pandas",
        "saspy",
        "pywin32"
    ],
    entry_points="""
    [console_scripts]
    target-sas7bdat=target-sas7bdat:main
    """,
    packages=["target-sas7bdat"],
    package_data = {},
    include_package_data=True,
)
