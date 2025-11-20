# Install package

from setuptools import setup, find_packages
setup(
    name='csbenchlab',
    version='0.1.0',
    packages=find_packages(),
    include_dirs=[
        "qt", 'csb_matlab', 'backend'
    ],
    install_requires=[
        'numpy',
        'scipy',
        'bdsim',
        'PyQt6',
    ],
    author='Your Name',
    description='A package for CSBenchLab',
    entry_points={
        'console_scripts': [
            'csb = csb:main',
            "csbenchlab = gui:main",
        ],
    },
    py_modules=['csb', 'gui'],
)
