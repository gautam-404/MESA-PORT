from setuptools import setup,find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name='MESAcommando',
    version='1.0',
    packages=find_packages(),
    install_requires=required,
    url='https://github.com/gautam-404/MESAcommando.git',
    author='gautam-404',
    description='Be a MESA commander!',
)
