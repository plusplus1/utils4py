from __future__ import print_function
from __future__ import unicode_literals

import re

from setuptools import find_packages, setup

with open('utils4py/__init__.py', 'r') as f:
    text = f.read()
    version = re.findall('^__version__[^\n]*\n$', text, re.M | re.S)[0].split("=", 1)[1].strip()  # type: str
    version = version.strip("\"\'")

classifiers = [
    'Programming Language :: Python :: 3',
]

setup(
    name="utils4py",
    version=version,
    description="A set of useful utilities for python",
    author='plusplus1',
    author_email='comeson@126.com',
    url='https://github.com/plusplus1/utils4py',
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    zip_safe=False,
    classifiers=classifiers,
    tests_require=["pytest"],
    install_requires=["six>=1.12.0",
                      "flask>=1.1.1",
                      "PyMySQL>=0.9.3",
                      "redis>=3.2.1",
                      "gevent>=1.4.0",
                      "pymongo==3.8.0",
                      "PyYAML>=5.1.1",
                      "requests>=2.22.0",
                      'redis-py-cluster==2.1.3',
                      ],
    python_requires='>=3.6',
)
