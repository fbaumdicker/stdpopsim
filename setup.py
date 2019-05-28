import os
import codecs
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='stdpopsim',
    description='Standard simulation models for msprime',
    long_description=long_description,
    author='PopSim Consortium',
    # TODO probably should have a different email address?
    author_email='popgen_benchmark@lists.uoregon.edu',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='simulations, recombination map, models',
    packages=['stdpopsim'],
    include_package_data=True,
    install_requires=["msprime", "appdirs"],
    url='https://github.com/popgensims/stdpopsim',
    project_urls={
        'Bug Reports': 'https://github.com/popgensims/stdpopsim/issues',
        'Source': 'https://github.com/tsckit-dev/stdpopsim',
    },
    license="MIT",
    platforms=["POSIX", "MacOS X", "Windows"],
    setup_requires=['setuptools_scm'],
    use_scm_version={"write_to": "stdpopsim/_version.py"},
)
