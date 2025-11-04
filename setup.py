# Install package

from setuptools import setup, find_packages
setup(
    name='csbenchlab',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scipy',
    ],
    author='Your Name',
)
