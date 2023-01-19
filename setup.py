from setuptools import setup,find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name='MESAmanager',
    version='1.0.0-beta',
    packages=find_packages(),
    install_requires=required,
    url='https://github.com/gautam-404/MESA-manager.git',
    author='gautam-404'
)
