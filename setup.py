"""``pvgeohdf``: An offshoot of PVGeo for HDF5 and netCDF data formats in ParaView
"""

import setuptools

__version__ = '0.0.1'

with open("README.rst", "r") as f:
    long_description = f.read()


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
    install_requires=[
        'PVGeo==1.1.35', # Developed in conjuction with PVGeo
        'numpy>=1.13',
        'scipy>=1.1',
        #'vtk>=8.1.1', # NOTE: windows users need to be in Python 3
    ],
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
