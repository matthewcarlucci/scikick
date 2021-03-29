import sys
from setuptools import setup, find_packages
from distutils.util import convert_path

main_ns = {}
ver_path = convert_path('scikick/version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

# check for python version
if sys.version_info < (3, 6):
    sys.exit('Python version >=3.6 is required')

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='scikick',
    version=main_ns['__version__'],
    description='Utility for executing collecitons of computational notebooks',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['scikick'],
    zip_safe=False,
    install_requires=[
        'snakemake>=5.9.0',
        'ruamel.yaml>=0.16.5',
        'graphviz>=0.16'
        ],
    include_package_data = True,
    entry_points={
        'console_scripts': [
            'sk = scikick.scikick:main'
        ]
    },
    test_suite='nose.collector',
    tests_require=['nose'],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: Unix",
        "Operating System :: POSIX :: Linux",
    ],
)
