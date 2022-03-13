#!/usr/bin/env python

from setuptools import setup
from pathlib import Path
import elastic_dql

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

packages = ['elastic_dql']
requires = ["djangoql==0.17.1", "elasticsearch==8.1.0"]

setup(
    name='elastic-dql',
    packages=packages,
    install_requires=requires,
    version=elastic_dql.__version__,
    description='Elastic query language library - convering readable queries to elasticsearch query',
    long_description_content_type='text/markdown',
    long_description=long_description,
    author='Mohammad Ahadi',
    author_email='mohammadahadi27s@gmail.com',
    url='https://github.com/mohammad-ahadi/elastic-dql',
    license=open('LICENSE').readline().strip(),
    zip_safe=False,

)
