HDF & netCDF I/O for PVGeo
==========================

.. image:: https://readthedocs.org/projects/pvgeo-hdf5/badge/?version=latest
   :target: http://hdf5.pvgeo.org
   :alt: Documentation Status

.. image:: https://img.shields.io/badge/docs%20by-gendocs-blue.svg
   :target: https://gendocs.readthedocs.io/en/latest/?badge=latest)
   :alt: Documentation Built by gendocs

.. image:: https://travis-ci.org/OpenGeoVis/PVGeo-HDF5.svg?branch=master
   :target: https://travis-ci.org/OpenGeoVis/PVGeo-HDF5
   :alt: Build Status

.. image:: https://img.shields.io/github/stars/OpenGeoVis/PVGeo-HDF5.svg?style=social&label=Stars
   :target: https://github.com/OpenGeoVis/PVGeo-HDF5
   :alt: GitHub

An offshoot of `PVGeo`_ for HDF5 and netCDF data formats.

.. admonition:: Why isn't this included in PVGeo?

    These features are experimental and we are concerned about how netCDF/HDF files
    do not have any inherit structure that might define spatially referenced data.
    We are also concerned that some of the dependancies for HDF5 I/O libraries
    might make PVGeo's installation process a bit cumbersome for the average user.

    If we find that this framework is simple, and doesn't add to much weight to PVGeo,
    then we will merge this project into a new suite within `PVGeo`_.


.. _PVGeo: http://pvgeo.org

This project is a work in progress!


Installation
------------

.. code-block:: bash

    git clone https://github.com/OpenGeoVis/PVGeo-HDF5.git
    cd PVGeo-HDF5

    pip install -e .


Examples
--------

Take a look at the notebook examples under the `examples directory`_

.. _examples directory: https://github.com/OpenGeoVis/PVGeo-HDF5/examples
