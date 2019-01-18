"""``pvgeohdf``: An offshoot of PVGeo for HDF5 and netCDF data formats in ParaView
"""

import setuptools
import warnings
import platform
import sys
import os

__version__ = '0.0.2'

with open("README.rst", "r") as f:
    long_description = f.read()


# Manage requirements
install_requires=[
    'PVGeo>=1.2.0',
    'numpy>=1.13',
    'scipy>=1.1',
    'colour-runner==0.0.5',
    'codecov==2.0.15',
    'vtk>=8.1.1',
    'netCDF4>=1.4.1',
]

# add vtk if not windows and (not Python 3.x or not x64)
if os.name == 'nt' and (int(sys.version[0]) < 3 or '64' not in platform.architecture()[0]):
    warnings.warn('\nYou will need to install VTK manually.' +
                  '  Try using Anaconda.  See:\n'
                  + 'https://anaconda.org/anaconda/vtk')
else:
    install_requires.append(['vtk>=8.1'])



setuptools.setup(
    name="pvgeohdf",
    version=__version__,
    author="Bane Sullivan",
    author_email="info@pvgeo.org",
    description="An offshoot of PVGeo for HDF5 and netCDF data formats readers in ParaView",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/OpenGeoVis/PVGeo-HDF5",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=(
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Scientific/Engineering :: GIS',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
    ),
)
