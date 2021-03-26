import re

from setuptools import find_packages, setup

extras_require = {}

version = None
with open('utils4py/__init__.py', 'r') as f:
    for line in f:
        m = re.match(r'^__version__\s*=\s*(["\'])([^"\']+)\1', line)
        if m:
            version = m.group(2)
            break
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
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    install_requires=[
        "six==1.12.0",
        "flask==1.1.1",
        "PyMySQL==0.9.3",
        "redis==3.2.1",
        "gevent>=1.4.0",
        "pymongo==3.8.0",
        "PyYAML==5.4",
        "requests>=2.22.0",
    ],
    extras_require=extras_require,
)
