from setuptools import setup, find_packages
from pecan.versions import pecan_version

setup(
    name="Pecan",
    version=pecan_version,
    packages=find_packages(),
    scripts=['pecan.py'],
    install_requires=['lark', 'colorama', 'IPython', 'matplotlib']
)

