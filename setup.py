from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='brainboost_data_source_package',
    version='1.0.0',
    author='Pablo Tomas Borda',
    author_email='pablotomasborda@gmail.com',
    description='A Python package for accessing data sources of different type (real time, on demand, Periodic).',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/brainboost-data-source-package',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Choose your license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'brainboost_data_source_logger_package',
        'brainboost_configuration_package'
    ],
    include_package_data=True,  # Include package data as specified in MANIFEST.in
)
