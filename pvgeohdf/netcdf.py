"""This module contains general readers and writers for netCDF formats."""

__all__ = [
    'SVCParcelReader',
]

__displayname__ = 'netCDF I/O'


import vtk
import numpy as np
from vtk.numpy_interface import dataset_adapter as dsa
import pandas as pd
import warnings

import netCDF4

# Import PVGeo helpers:
from PVGeo.base import ReaderBaseBase
from PVGeo import _helpers
from PVGeo import interface

# Import internal helpers:
from .base import netCDFPointsReaderBase


###############################################################################
# SVC Parcels

class SVCParcelReader(netCDFPointsReaderBase):
    """SVCParcelReader for Kelton"""
    __displayname__ = 'SVC Parcel Reader'
    __category__ = 'reader'
    def __init__(self, **kwargs):
        ReaderBaseBase.__init__(self, nOutputPorts=1, outputType='vtkPolyData', **kwargs)
        self._dataName = kwargs.get('name', 'Data')
        self._keys = []

    #### File reading methods ####


    def _ReadUpFront(self):
        """This parses the loaded dataset to a NumPy ndarray. The first axis
        represents a time step in the model space.
        """
        # Perform Read
        self._GetFileContents()

        ###############################################
        # TODO: this needs to be generalized for any array names
        # Allow this to be chosen by user:
        poskeys = ["parcel_x_pos", "parcel_y_pos", "parcel_z_pos"]
        ###############################
        x_pos2 = self._dataSet.variables[poskeys[0]]
        y_pos2 = self._dataSet.variables[poskeys[1]]
        z_pos2 = self._dataSet.variables[poskeys[2]]

        tshape = x_pos2.shape[1]
        num = x_pos2.shape[0]
        self._timesteps = [i for i in range(tshape)]

        # Now get the rest of the data
        self._keys = list(self._dataSet.variables.keys())
        dataArrs = dict()
        for k in list(self._dataSet.variables.keys()):
            if k not in poskeys:
                dataArrs.setdefault(k, self._dataSet.variables[k])
        nAtts = len(dataArrs.keys())

        # 3D array where first axis is time
        # and second-third axii are basically a table of XYZ+attributes
        self._data = np.zeros((tshape, num, 3 + nAtts))
        # Add the XYZ points first by convention for PVGeo
        self._data[:, :, 0] = np.array(x_pos2).swapaxes(0,1)
        self._data[:, :, 1] = np.array(y_pos2).swapaxes(0,1)
        self._data[:, :, 2] = np.array(z_pos2).swapaxes(0,1)
        # Now append all the data arrays
        i = 3
        self._keys = []
        for name, d in dataArrs.items():
            self._data[:, :, i] = np.array(d).swapaxes(0,1)
            self._keys.append(name)
            i += 1
        # Mark as read
        self.NeedToRead(flag=False)
        return 1


    def _GetRawData(self, idx=0):
        """Get the Points as numpy ndarrays or pandas dataframe where first three
        columns are the XYZ coordinates
        """
        # Get the time step then make a data frame
        data = self._data[idx, :, :]
        names = ["X", "Y", "Z"] + self._keys
        df = pd.DataFrame(data=data, columns=names)
        return df



    #### Getters/Setters ####

    def SetDataName(self, name):
        """This is an example of how to set a property for this reader to use.
        Note that we do not use this property.
        """
        # WARNING: You must call ``self.Modified`` like below
        if self._dataName != name:
            self._dataName = name
            self.Modified(readAgain=False)
