from setuptools import setup, find_packages

setup(
    name="serPy",  # Name of your package
    version="0.1.0",  # Initial version
    description="A library for manipulating SER files in Python.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",  # Use Markdown for PyPI
    author="Jason Niles",
    url="https://github.com/gravitylens/serPy",  # GitHub repository link
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "opencv-python-headless",
        "Pillow",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Minimum Python version
)
