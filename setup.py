# -*- coding: utf-8 -*-
import pathlib

import packutil as pack
from setuptools import find_packages, setup

# write version on the fly - inspired by numpy
MAJOR = 0
MINOR = 4
MICRO = 3

repo_path = pathlib.Path(__file__).absolute().parent


def setup_package():
    # write version
    pack.versions.write_version_py(
        MAJOR,
        MINOR,
        MICRO,
        pack.versions.is_released(repo_path),
        filename="src/banana/version.py",
    )
    # paste Readme
    with open("README.md", "r") as fh:
        long_description = fh.read()
    # do it
    setup(
        name="banana-hep",
        author="Felix Hekhorn, Alessandro Candido, Giacomo Magni, Andrea Barontini",
        version=pack.versions.mkversion(MAJOR, MINOR, MICRO),
        long_description=long_description,
        long_description_content_type="text/markdown",
        author_email="",
        url="https://github.com/N3PDF/banana",
        description="mm yummy banana",
        package_dir={"": "src"},
        packages=find_packages("src"),
        package_data={
            "banana": [
                "data/templatePDF.dat",
                "data/templatePDF.info",
                "data/theory_template.yaml",
            ]
        },
        classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Topic :: Scientific/Engineering",
            "Topic :: Scientific/Engineering :: Physics",
        ],
        install_requires=[
            "ipython",
            "SQLAlchemy",
            "numpy",
            "pandas",
            "matplotlib",
            "jinja2",
            "rich",
            "pyyaml",
            "human_dates2",
            "click",
            "eko",
        ],
        entry_points={
            "console_scripts": [
                "generate_pdf=banana.data.generate_pdf:generate_pdf",
                "install_pdf=banana.data.generate_pdf:install_pdf",
                "genpdf=banana.data.genpdf.cli:cli",
            ],
        },
        python_requires=">=3.7",
    )


if __name__ == "__main__":
    setup_package()
