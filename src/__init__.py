# source file
from setuptools import setup, find_packages

setup(
    name="BattleShip",
    version="1.0.0",
    description="A BattleShip game project",
    author="Alberto Giacomel",
    author_email="alberto.giacomel@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[],
    extras_require={
        "dev": ["flask", "pandas", "uuid"]
    },
    entry_points={
        "console_scripts": [
            "run_app=src.battaglia:main"
        ]
    },
)
