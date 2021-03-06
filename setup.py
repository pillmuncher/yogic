# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.21a'
__date__ = '2021-04-22'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

from setuptools import setup, find_packages

if __name__ == '__main__':
    setup(
        packages=find_packages(where='src'),
        package_dir={'':'src'}
    )
