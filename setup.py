from setuptools import find_packages, setup

extras_require = {}

setup(
    name="utils4py",
    version="0.1.1",
    description="A set of useful utilities for python",
    author='plusplus1',
    author_email='comeson@126.com',
    url='https://github.com/plusplus1/utils4py',
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    zip_safe=False,
    # entry_points={
    #     'console_scripts': []
    # },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    install_requires=[
        "six>=1.10.0",
        "flask>=1.0.2",
        "PyMySQL>=0.8.1",
        "redis>=2.10.6",
    ],
    extras_require=extras_require,
)
