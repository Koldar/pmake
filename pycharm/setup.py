import setuptools
import version

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("LIECENSE.md", "r", encoding="utf-8") as fh:
    license = fh.read()

setuptools.setup(
    name="pmake", # Replace with your own username
    version=version.VERSION,
    author="Massimo Bono",
    author_email="massimobono1@gmail.com",
    description="Library for quickly develop makefile-like files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=license,
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    scripts=['scripts/pmake.py'],
    python_requires='>=3.6',
)