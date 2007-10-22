
from setuptools import setup

setup(
    name = 'djog',
    # TODO: dynamically create from djog, but internal dependancies will play
    # out first.
    version = '0.1_pre',
    packages = ['djog', 'djog.templatetags',],
    url = 'http://dev.oebfare.com/projects/djog/',
    classifiers = ['Programming Language :: Python',]
)
