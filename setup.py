from setuptools import setup, find_packages

setup(
    name="whatson",
    author="Simon Walker",
    author_email="s.r.walker101@googlemail.com",
    version="0.0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "whatson-ingest = whatson.ingest:main",
            "whatson-reset = whatson.models:reset",
        ]
    },
)
