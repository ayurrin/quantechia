from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='quantechia',
    version='0.1.0',
    packages=find_packages(include=['quantechia', 'quantechia.*']),
    install_requires=requirements,
)
    packages=find_packages(include=['quantechia', 'quantechia.*']),
    install_requires=requirements,
)
