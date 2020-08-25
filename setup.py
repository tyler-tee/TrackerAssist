from setuptools import setup
from os import path

current_direct = path.abspath(path.dirname(__file__))
with open(path.join(current_direct, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='TrackerAssist',
    version='0.1.5',
    packages=['TrackerAssist'],
    url='https://github.com/tyler-tee/trackerassist',
    license='GPLv3',
    author='Tyler Talaga',
    author_email='ttalaga@wgu.edu',
    description='TrackerAsisst is a Python library for interacting with Request Tracker\'s REST API 2.0 (pre-installed as of RT 5.0.0).',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
