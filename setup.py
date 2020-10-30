# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

# write version on the fly - inspired by numpy
MAJOR = 0
MINOR = 1
MICRO = 4
ISRELEASED = False
SHORT_VERSION = "%d.%d" % (MAJOR, MINOR)
VERSION = "%d.%d.%d" % (MAJOR, MINOR, MICRO)


def write_version_py(filename="src/banana/version.py"):
    cnt = """
# THIS FILE IS GENERATED FROM SETUP.PY
major = %(major)d
short_version = '%(short_version)s'
version = '%(version)s'
full_version = '%(full_version)s'
is_released = %(isreleased)s
"""
    FULLVERSION = VERSION
    if not ISRELEASED:
        FULLVERSION += "-develop"

    a = open(filename, "w")
    try:
        a.write(
            cnt
            % {
                "major": MAJOR,
                "short_version": SHORT_VERSION,
                "version": VERSION,
                "full_version": FULLVERSION,
                "isreleased": str(ISRELEASED),
            }
        )
    finally:
        a.close()


def setup_package():
    # write version
    write_version_py()
    # paste Readme
    with open("README.md", "r") as fh:
        long_description = fh.read()
    # do it
    setup(
        name="banana-hep",
        author="Felix Hekhorn, Alessandro Candido",
        version=VERSION,
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
            "numpy",
            "pandas",
            "rich",
            "pyyaml",
            "tinydb~=4.1",
            "human_dates2",
        ],
        entry_points={
            "console_scripts": [
                "generate_pdf=banana.data.generate_pdf:generate_pdf",
                "install_pdf=banana.data.generate_pdf:install_pdf",
            ],
        },
        python_requires=">=3.7",
    )


if __name__ == "__main__":
    setup_package()
