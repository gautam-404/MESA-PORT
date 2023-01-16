from setuptools import setup,find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name='MESAmanager',
    version='0.3',
    packages=find_packages(),
    install_requires=required,
    url='https://github.com/gautam-404/MESAmanager.git',
    author='gautam-404'
)
