paraview_plugin_version = '0.1.0'
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

    @smproperty.xml(_helpers.get_file_reader_xml(SVCParcelReader.extensions, reader_description=SVC_DESC))
    def add_file_name(self, fname):
        SVCParcelReader.add_file_name(self, fname)

    # @smproperty.doublevector(name="TimeDelta", default_values=1.0, panel_visibility="advanced")
    # def SetTimeDelta(self, dt):
    #     SVCParcelReader.SetTimeDelta(self, dt)

    @smproperty.doublevector(name="TimestepValues", information_only="1", si_class="vtkSITimeStepsProperty")
    def get_time_step_values(self):
        """This is critical for registering the timesteps"""
        return SVCParcelReader.get_time_step_values(self)

    # This is an example of how to create a GUI input field
    @smproperty.stringvector(name='DataName', default_values='Data')
    def set_data_name(self, name):
        SVCParcelReader.set_data_name(self, name)


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

    @smproperty.xml(_helpers.get_file_reader_xml(CMAQReader.extensions, reader_description=SVC_DESC))
    def add_file_name(self, fname):
        CMAQReader.add_file_name(self, fname)

    # @smproperty.doublevector(name="TimeDelta", default_values=1.0, panel_visibility="advanced")
    # def set_time_delta(self, dt):
    #     CMAQReader.set_time_delta(self, dt)

    @smproperty.doublevector(name="TimestepValues", information_only="1", si_class="vtkSITimeStepsProperty")
    def get_time_step_values(self):
        """This is critical for registering the timesteps"""
        return CMAQReader.get_time_step_values(self)

    @smproperty.doublevector(name="Spacing", default_values=[1.0, 1.0, 1.0],)
    def set_spacing(self, dx, dy, dz):
        CMAQReader.set_spacing(self, dx, dy, dz)

    @smproperty.doublevector(name="Origin", default_values=[0.0, 0.0, 0.0],)
    def set_origin(self, ox, oy, oz):
        CMAQReader.set_origin(self, ox, oy, oz)
