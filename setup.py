
from setuptools import setup

version_bits = __import__('djog').VERSION
if version_bits[2] is not None:
    version = '%d.%d_%s' % version_bits
else:
    version = '%d.%d' % version_bits[:2]

setup(
    name = 'djog',
    version = version,
    packages = ['djog', 'djog.templatetags',],
    url = 'http://dev.oebfare.com/projects/djog/',
    classifiers = ['Programming Language :: Python',]
)
