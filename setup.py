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
    #     'console_scripts': ['scrapy = scrapy.cmdline:execute']
    # },
    # classifiers=[
    #     'Framework :: Scrapy',
    #     'Development Status :: 5 - Production/Stable',
    #     'Environment :: Console',
    #     'Intended Audience :: Developers',
    #     'License :: OSI Approved :: BSD License',
    #     'Operating System :: OS Independent',
    #     'Programming Language :: Python',
    #     'Programming Language :: Python :: 2',
    #     'Programming Language :: Python :: 2.7',
    #     'Programming Language :: Python :: 3',
    #     'Programming Language :: Python :: 3.4',
    #     'Programming Language :: Python :: 3.5',
    #     'Programming Language :: Python :: 3.6',
    #     'Programming Language :: Python :: Implementation :: CPython',
    #     'Programming Language :: Python :: Implementation :: PyPy',
    #     'Topic :: Internet :: WWW/HTTP',
    #     'Topic :: Software Development :: Libraries :: Application Frameworks',
    #     'Topic :: Software Development :: Libraries :: Python Modules',
    # ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    install_requires=[
        "six",
        "flask",
    ],
    extras_require=extras_require,
)
