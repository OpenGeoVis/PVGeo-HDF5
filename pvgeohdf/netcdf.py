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
from PVGeo.base import ReaderBase, ReaderBaseBase
from PVGeo.readers import DelimitedTextReader
from PVGeo import _helpers
from PVGeo import interface


###############################################################################
# SVC Parcels

class SVCParcelReader(ReaderBaseBase):
    """SVCParcelReader for Kelton"""
    __displayname__ = 'SVC Parcel Reader'
    __category__ = 'reader'
    extensions = 'nc netCDF netcdf'
    def __init__(self, **kwargs):
        ReaderBaseBase.__init__(self, nOutputPorts=1, outputType='vtkPolyData', **kwargs)
        self.__timesteps = [] # Initialize as empty
        self.__dataName = kwargs.get('name', 'Data')
        self.__data = None
        self.__dataSet = None
        self.__keys = []

    #### File reading methods ####

    def GetFileName(self):
        """Super class has file names as a list but we will only handle a single
        project file. This provides a conveinant way of making sure we only
        access that single file.
        A user could still access the list of file names using ``GetFileNames()``.
        """
        return ReaderBaseBase.GetFileNames(self, idx=0)

    def _GetFileContents(self, idx=None):
        """This happens up front so the data read happens only once and ParaView
        will be able to make calls on the ``RequestData`` method to get the data
        for a specific timestep"""
        self.__dataSet = netCDF4.Dataset(self.GetFileName())
        return 1

    def _ReadUpFront(self):
        """This parses the file contents to numpy ndarray. The first axis
        represents a time step in the model space.
        """
        # Perform Read
        self._GetFileContents()

        ###############################################
        # TODO: this needs to be generalized with for any array names
        # Allow this to be chosen by user:
        poskeys = ["parcel_x_pos", "parcel_y_pos", "parcel_z_pos"]
        ###############################
        x_pos2 = self.__dataSet.variables[poskeys[0]]
        y_pos2 = self.__dataSet.variables[poskeys[1]]
        z_pos2 = self.__dataSet.variables[poskeys[2]]

        tshape = x_pos2.shape[1]
        num = x_pos2.shape[0]
        self.__timesteps = [i for i in range(tshape)]

        # Now get the rest of the data
        self.__keys = list(self.__dataSet.variables.keys())
        dataArrs = dict()
        for k in list(self.__dataSet.variables.keys()):
            if k not in poskeys:
                dataArrs.setdefault(k, self.__dataSet.variables[k])

        nAtts = len(dataArrs.keys())

        # 3D array where first axis is time
        # and second-third axii are basically a table of XYZ+attributes
        self.__data = np.zeros((tshape, num, 3 + nAtts))
        # Add the XYZ points first by convention for PVGeo
        self.__data[:, :, 0] = np.array(x_pos2).swapaxes(0,1)
        self.__data[:, :, 1] = np.array(y_pos2).swapaxes(0,1)
        self.__data[:, :, 2] = np.array(z_pos2).swapaxes(0,1)
        # Now append all the data arrays
        i = 3
        self.__keys = []
        for name, d in dataArrs.items():
            self.__data[:, :, i] = np.array(d).swapaxes(0,1)
            self.__keys.append(name)
            i += 1
        # Mark as read
        self.NeedToRead(flag=False)
        return 1


    def _GetRawData(self, idx=0):
        """Get the Points as numpy ndarrays or pandas dataframe where first three
        columns are the XYZ coordinates
        """
        # Get the time step then make a data frame
        data = self.__data[idx, :, :]
        names = ["X", "Y", "Z"] + self.__keys
        df = pd.DataFrame(data=data, columns=names)
        return df

    #### Algorithm Methods ####

    def RequestData(self, request, inInfo, outInfo):
        """Used by pipeline to get data for current timestep and populate the output data object.
        """
        # Get output:
        output = self.GetOutputData(outInfo, 0)
        # Get requested time index
        i = _helpers.getRequestedTime(self, outInfo)
        if self.NeedToRead():
            self._ReadUpFront()
        # Get the data which has already been loaded
        data = self._GetRawData(idx=i) # these should just be XYZ+attribute
        #   in either a numpy array or a pandas dataframe where first three
        #   columns are the XYZ arrays
        output.DeepCopy(interface.pointsToPolyData(data))
        return 1 # NOTE: ALWAYS return 1 on pipeline methods


    def _UpdateTimeSteps(self):
        """For internal use only: appropriately sets the timesteps.
        """
        if self.NeedToRead():
            self._ReadUpFront()
        # NOTE: Assumes self._ReadUpFront() handls timestep generation
        if len(self.__timesteps) > 1:
            executive = self.GetExecutive()
            oi = executive.GetOutputInformation(0)
            #oi = outInfo.GetInformationObject(0)
            oi.Remove(executive.TIME_STEPS())
            oi.Remove(executive.TIME_RANGE())
            for t in self.__timesteps:
                oi.Append(executive.TIME_STEPS(), t)
            oi.Append(executive.TIME_RANGE(), self.__timesteps[0])
            oi.Append(executive.TIME_RANGE(), self.__timesteps[-1])
        return 1 # NOTE: ALWAYS return 1 on pipeline methods


    def RequestInformation(self, request, inInfo, outInfo):
        """This is a convenience method that should be overwritten when needed.
        This will handle setting the timesteps appropriately based on the number
        of file names when the pipeline needs to know the time information.
        """
        if self.NeedToRead():
            self._ReadUpFront()
        self._UpdateTimeSteps()
        return 1 # NOTE: ALWAYS return 1 on pipeline methods

    #### Getters/Setters ####

    def SetDataName(self, name):
        """This is an example of how to set a property for this reader to use
        """
        # WARNING: You must call ``self.Modified`` like below
        if self.__dataName != name:
            self.__dataName = name
            self.Modified(readAgain=False)


    def GetTimestepValues(self):
        """Use this in ParaView decorator to register timesteps on the pipeline.
        """
        if self.NeedToRead():
            self._ReadUpFront()
        return self.__timesteps if self.__timesteps is not None else None
