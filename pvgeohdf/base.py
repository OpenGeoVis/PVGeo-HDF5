"""These provide base classes to simplify making new classes."""

__all__ = [
    'netCDFReaderBase',
    'netCDFPointsReaderBase',
]

__displayname__ = 'Base Classes'

import netCDF4

# Import PVGeo helpers:
from PVGeo.base import ReaderBaseBase
from PVGeo import _helpers
from PVGeo import interface




class netCDFReaderBase(ReaderBaseBase):
    """netCDFReaderBase"""
    __displayname__ = 'net CDF Reader Base'
    __category__ = 'base'
    extensions = 'nc netCDF netcdf'
    def __init__(self, nOutputPorts=1, outputType='vtkPolyData', **kwargs):
        ReaderBaseBase.__init__(self, nOutputPorts=nOutputPorts, outputType=outputType, **kwargs)
        self._timesteps = [] # Initialize as empty
        self._data = None
        self._dataSet = None
        self._keys = []

    #### File reading methods ####

    def GetFileName(self):
        """Super class has file names as a list but we will only handle a single
        netCDF file. This provides a conveinant way of making sure we only
        access that single file. A user could still access the list of file
        names using ``GetFileNames()``.
        """
        return ReaderBaseBase.GetFileNames(self, idx=0)

    def _GetFileContents(self, idx=None):
        """This opens a netCDF4 DataSet.
        This happens up front so the data read happens only once and ParaView
        will be able to make calls on the ``RequestData`` method to get the data
        for a specific timestep"""
        self._dataSet = netCDF4.Dataset(self.GetFileName())
        return 1

    def _ReadUpFront(self):
        """OVERRIDE: This parses the loaded dataset.
        """
        # Perform Read
        self._GetFileContents()
        raise NotImplementedError('Code me up!')
        # Mark as read
        self.NeedToRead(flag=False)
        return 1


    def _GetRawData(self, idx=0):
        """Get the data as the called for data object. Return type depends on
        higher level API.

        Args:
            idx (int): the timestep index
        """
        # Get the time step then make a data frame
        raise NotImplementedError('Code me up!')
        #data = self._data[???]
        return data

    #### Algorithm Methods ####

    def RequestData(self, request, inInfo, outInfo):
        """Used by pipeline to get data for current timestep and populate the
        output data object.
        """
        # Get output:
        output = self.GetOutputData(outInfo, 0)
        # Get requested time index
        i = _helpers.getRequestedTime(self, outInfo)
        if self.NeedToRead():
            self._ReadUpFront()
        raise NotImplementedError('Code me up!')
        return 1 # NOTE: ALWAYS return 1 on pipeline methods


    def _UpdateTimeSteps(self):
        """For internal use only: appropriately sets the timesteps.
        """
        if self.NeedToRead():
            self._ReadUpFront()
        # NOTE: Assumes self._ReadUpFront() handls timestep generation
        if len(self._timesteps) > 1:
            executive = self.GetExecutive()
            oi = executive.GetOutputInformation(0)
            #oi = outInfo.GetInformationObject(0)
            oi.Remove(executive.TIME_STEPS())
            oi.Remove(executive.TIME_RANGE())
            for t in self._timesteps:
                oi.Append(executive.TIME_STEPS(), t)
            oi.Append(executive.TIME_RANGE(), self._timesteps[0])
            oi.Append(executive.TIME_RANGE(), self._timesteps[-1])
        return 1 # NOTE: ALWAYS return 1 on pipeline methods


    def RequestInformation(self, request, inInfo, outInfo):
        """This will handle setting the timesteps appropriately based on the number
        of file names when the pipeline needs to know the time information.
        """
        if self.NeedToRead():
            self._ReadUpFront()
        self._UpdateTimeSteps()
        return 1 # NOTE: ALWAYS return 1 on pipeline methods


    #### Getters/Setters ####


    def GetTimestepValues(self):
        """Use this in ParaView decorator to register timesteps on the pipeline.
        """
        if self.NeedToRead():
            self._ReadUpFront()
        return self._timesteps if self._timesteps is not None else None




class netCDFPointsReaderBase(netCDFReaderBase):
    """netCDFPointsReaderBase: for netCDF files that will produce a
    point+attribute dataset."""
    __displayname__ = 'netCDF Points Reader Base'
    __category__ = 'base'
    def __init__(self, nOutputPorts=1, outputType='vtkPolyData', **kwargs):
        netCDFReaderBase.__init__(self, nOutputPorts=nOutputPorts, outputType=outputType, **kwargs)


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
        data = self._GetRawData(idx=i) # these should just be XYZ+attribute
        #   in either a numpy array or a pandas dataframe where first three
        #   columns are the XYZ arrays
        output.DeepCopy(interface.pointsToPolyData(data))
        return 1 # NOTE: ALWAYS return 1 on pipeline methods
