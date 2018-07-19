'''
The setup.py file for larpix-reconstruction.

'''

from setuptools import setup, find_packages
from codecs import open
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
        name='larpix-reconstruction',
        version='0.0.0',
        description='Rebuild events from LArPix data',
        long_description=long_description,
        url='https://github.com/samkohn/larpix-reconstruction',
        author='Peter Madigan',
        author_email='pmadigan@lbl.gov',
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
        ],
        keywords='dune physics',
        packages=['larpixreco'],
        install_requires=['pytest', 'h5py', 'numpy', 'sympy'],
)
