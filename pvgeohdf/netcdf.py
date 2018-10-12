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
    extensions = 'netCDF netcdf'
    def __init__(self, **kwargs):
        ReaderBaseBase.__init__(self, nOutputPorts=1, outputType='vtkPolyData', **kwargs)
        self.__timesteps = [] # Initialize as empty
        self.__dataName = kwargs.get('name', 'Data')

    #### File reading methods ####

    def _GetFileContents(self, idx=None):
        """This happens up front so the data read happens only once and ParaView
        will be able to make calls on the ``RequestData`` method to get the data
        for a specific timestep"""
        raise NotImplementedError('Code me up!')

    def _ReadUpFront(self):
        """Override to handle making time series of the different data arrays
        """
        # Perform Read
        contents = self._GetFileContents()

        # TODO: we need to set self.__timesteps here
        #       It should simply by a list of the time steps to use

        self.NeedToRead(flag=False)
        return 1


    def _GetRawData(self, idx=0):
        """Get the Points as numpy ndarrays or pandas dataframe where first three
        columns are the XYZ coordinates
        """
        raise NotImplementedError('Code me up!')


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
