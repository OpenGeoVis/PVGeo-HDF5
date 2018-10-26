"""This module contains general readers and writers for netCDF formats."""

__all__ = [
    'SVCParcelReader',
    'CMAQReader',
]

__displayname__ = 'netCDF I/O'


import numpy as np
import pandas as pd
import netCDF4
import vtk

# Import PVGeo helpers:
from PVGeo.base import ReaderBaseBase
from PVGeo import _helpers
from PVGeo import interface

# Import internal helpers:
from .base import netCDFPointsReaderBase, netCDFReaderBase


###############################################################################
# SVC Parcels

class SVCParcelReader(netCDFPointsReaderBase):
    """SVCParcelReader for Kelton"""
    __displayname__ = 'SVC Parcel Reader'
    __category__ = 'reader'
    def __init__(self, **kwargs):
        netCDFPointsReaderBase.__init__(self, nOutputPorts=1, outputType='vtkPolyData', **kwargs)
        self._dataName = kwargs.get('name', 'Data')

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


###############################################################################
# CMAQ

class CMAQReader(netCDFReaderBase):
    """CMAQ read for Ziwei Wu"""
    __displayname__ = 'CMAQ Reader'
    __category__ = 'reader'
    def __init__(self, **kwargs):
        netCDFReaderBase.__init__(self, nOutputPorts=1, outputType='vtkImageData', **kwargs)
        self.__shp = None
        self.__spacing = [1.0, 1.0, 1.0]
        self.__origin = [0.0, 0.0, 0.0]

    #### File reading methods ####


    def _ReadUpFront(self):
        """This parses the loaded dataset to a NumPy ndarray. The first axis
        represents a time step in the model space.
        """
        # Perform Read
        self._GetFileContents()
        # Set up time shape
        tflag = self._dataSet.variables['TFLAG']
        tshape = tflag.shape[0]
        # TODO: actually use the time step values from the data file
        self._timesteps = [i for i in range(tshape)]

        # Now get the rest of the data
        self._keys = list(self._dataSet.variables.keys())
        self._keys.remove('TFLAG') # Remove tflag in place
        dataArrs = dict()
        self.__shp = self._dataSet.variables[self._keys[0]].shape
        num = self.__shp[1] * self.__shp[2] * self.__shp[3]
        for k in self._keys:
            d = np.array(self._dataSet.variables[k])
            # Swap the axis
            dataArrs.setdefault(k, d.reshape((tshape, -1)))
            if d.shape != self.__shp:
                raise RuntimeError('Dimension mismatch in the dataset')
        nAtts = len(dataArrs.keys())

        # 3D array where first axis is time
        # and second-third axii are basically a table of the flattened attributes
        self._data = np.zeros((tshape, num, nAtts))
        # Now append all the data arrays
        for i, k in enumerate(self._keys):
            self._data[:, :, i] = np.array(dataArrs[k])
        # Mark as read
        self.NeedToRead(flag=False)
        return 1


    def _GetRawData(self, idx=0):
        """Get the Points as numpy ndarrays or pandas dataframe where first three
        columns are the XYZ coordinates
        """
        # Get the time step then make a data frame
        data = self._data[idx, :, :]
        df = pd.DataFrame(data=data, columns=self._keys)
        return df

    def GetExtent(self, dim=False):
        if self.__shp is None:
            self._ReadUpFront()
        nz, ny, nx = self.__shp[1::]
        if dim:
            return (nx, ny, nz)
        return (0,nx, 0,ny, 0,nz)


    #### Algorithm Methods ####

    def RequestData(self, request, inInfo, outInfo):
        """Used by pipeline to get data for current timestep and populate the
        output data object. This assumes that ``self._GetRawData()`` will return
        a dataset ready for PVGeo's ``interface.pointsToPolyData()``.
        """
        # Get output:
        output = self.GetOutputData(outInfo, 0)
        # Get requested time index
        i = _helpers.getRequestedTime(self, outInfo)
        if self.NeedToRead():
            self._ReadUpFront()
        # Get the data which has already been loaded
        data = self._GetRawData(idx=i)
        # Generate the data object
        nx, ny, nz = self.GetExtent(dim=True)
        dx, dy, dz = self.__spacing
        ox, oy, oz = self.__origin
        output.SetDimensions(nx+1, ny+1, nz+1)
        output.SetSpacing(dx, dy, dz)
        output.SetOrigin(ox, oy, oz)
        # Use table generater and convert because its easy:
        table = vtk.vtkTable()
        interface.dataFrameToTable(data, table)
        # now get arrays from table and add to cell data of output
        for i in range(table.GetNumberOfColumns()):
            output.GetCellData().AddArray(table.GetColumn(i))
        del(table)
        return 1 # NOTE: ALWAYS return 1 on pipeline methods


    def RequestInformation(self, request, inInfo, outInfo):
        """Used by pipeline to set grid extents.
        """
        # Call parent to handle time stuff
        netCDFReaderBase.RequestInformation(self, request, inInfo, outInfo)
        # Now set whole output extent
        if self.NeedToRead():
            self._ReadUpFront()
        ext = self.GetExtent()
        info = outInfo.GetInformationObject(0)
        # Set WHOLE_EXTENT: This is absolutely necessary
        info.Set(vtk.vtkStreamingDemandDrivenPipeline.WHOLE_EXTENT(), ext, 6)
        return 1


    def SetSpacing(self, dx, dy, dz):
        """Set the spacing for each axial direction"""
        spac = (dx, dy, dz)
        if self.__spacing != spac:
            self.__spacing = spac
            self.Modified(readAgain=False)

    def SetOrigin(self, ox, oy, oz):
        """Set the origin corner of the grid"""
        origin = (ox, oy, oz)
        if self.__origin != origin:
            self.__origin = origin
            self.Modified(readAgain=False)
