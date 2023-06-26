from __future__ import print_function
from __future__ import unicode_literals

import re
import sys

from setuptools import find_packages, setup

with open('utils4py/__init__.py', 'r') as f:
    text = f.read()
    version = re.findall('^__version__[^\n]*\n$', text, re.M | re.S)[0].split("=", 1)[1].strip()  # type: str
    version = version.strip("\"\'")

classifiers = [
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
]

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY2:
    install_requires = ["six>=1.12.0",
                        "flask<=1.1.4,>=1.1.1",
                        "PyMySQL<1.0.0,>=0.9.3",
                        "redis<=3.5.3,>=3.2.1",
                        "gevent>=1.4.0",
                        "pymongo==3.8.0",
                        "PyYAML<=5.4.1,>=5.1.1",
                        "requests<2.28.0,>=2.22.0",
                        'redis-py-cluster==2.1.3',
                        ]
else:
    install_requires = ["six>=1.12.0",
                        "flask>=1.1.1",
                        "PyMySQL>=0.9.3",
                        "redis>=3.2.1",
                        "gevent>=1.4.0",
                        "pymongo==3.8.0",
                        "PyYAML>=5.1.1",
                        "requests>=2.22.0",
                        'redis-py-cluster==2.1.3',
                        ]

tests_require = ["pytest"]

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
    tests_require=tests_require,
    install_requires=install_requires,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
)
