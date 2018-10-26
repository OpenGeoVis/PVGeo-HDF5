paraview_plugin_version = '0.0.1'
# This is module to import. It provides VTKPythonAlgorithmBase, the base class
# for all python-based vtkAlgorithm subclasses in VTK and decorators used to
# 'register' the algorithm with ParaView along with information about UI.
from paraview.util.vtkAlgorithm import *

import sys
sys.path.append('/Users/bane/Documents/OpenGeoVis/Software/PVGeo-HDF5')

from pvgeohdf.netcdf import *


# Helpers:
from PVGeo import _helpers
# Classes to Decorate
from PVGeo.grids import *


#### GLOBAL VARIABLES ####
MENU_CAT = 'PVGeo-HDF'



###############################################################################

SVC_DESC = "SVC Parcel Reader: Time varying point cloud"

@smproxy.reader(name="PVGeoHDFSVCParcelReader",
       label="PVGeo: SVC Parcel Reader",
       extensions=SVCParcelReader.extensions,
       file_description=SVC_DESC)
class PVGeoHDFSVCParcelReader(SVCParcelReader):
    def __init__(self):
        SVCParcelReader.__init__(self)

    #### Seters and Geters ####

    @smproperty.xml(_helpers.getFileReaderXml(SVCParcelReader.extensions, readerDescription=SVC_DESC))
    def AddFileName(self, fname):
        SVCParcelReader.AddFileName(self, fname)

    # @smproperty.doublevector(name="TimeDelta", default_values=1.0, panel_visibility="advanced")
    # def SetTimeDelta(self, dt):
    #     SVCParcelReader.SetTimeDelta(self, dt)

    @smproperty.doublevector(name="TimestepValues", information_only="1", si_class="vtkSITimeStepsProperty")
    def GetTimestepValues(self):
        """This is critical for registering the timesteps"""
        return SVCParcelReader.GetTimestepValues(self)

    # This is an example of how to create a GUI input field
    @smproperty.stringvector(name='DataName', default_values='Data')
    def SetDataName(self, name):
        SVCParcelReader.SetDataName(self, name)


###############################################################################

SVC_DESC = "CMAQ Reader: Time varying grid"

@smproxy.reader(name="PVGeoCMAQReader",
       label="PVGeo: CMAQ Reader",
       extensions=CMAQReader.extensions,
       file_description=SVC_DESC)
class PVGeoCMAQReader(CMAQReader):
    def __init__(self):
        CMAQReader.__init__(self)

    #### Seters and Geters ####

    @smproperty.xml(_helpers.getFileReaderXml(CMAQReader.extensions, readerDescription=SVC_DESC))
    def AddFileName(self, fname):
        CMAQReader.AddFileName(self, fname)

    # @smproperty.doublevector(name="TimeDelta", default_values=1.0, panel_visibility="advanced")
    # def SetTimeDelta(self, dt):
    #     CMAQReader.SetTimeDelta(self, dt)

    @smproperty.doublevector(name="TimestepValues", information_only="1", si_class="vtkSITimeStepsProperty")
    def GetTimestepValues(self):
        """This is critical for registering the timesteps"""
        return CMAQReader.GetTimestepValues(self)

    @smproperty.doublevector(name="Spacing", default_values=[1.0, 1.0, 1.0],)
    def SetSpacing(self, dx, dy, dz):
        CMAQReader.SetSpacing(self, dx, dy, dz)

    @smproperty.doublevector(name="Origin", default_values=[0.0, 0.0, 0.0],)
    def SetOrigin(self, ox, oy, oz):
        CMAQReader.SetOrigin(self, ox, oy, oz)
