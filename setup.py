from setuptools import setup, find_packages

setup(
    name="Pecan",
    version="1.1.1",
    packages=find_packages(),
    scripts=['pecan.py'],
    install_requires=['lark', 'colorama', 'IPython', 'matplotlib']
)

