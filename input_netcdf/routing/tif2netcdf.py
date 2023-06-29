#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      burekpe
#
# Created:     16/01/2015
# Copyright:   (c) burekpe 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import numpy as np
from netCDF4 import Dataset
from netCDF4 import num2date, date2num
import time as timex
import datetime as date

#from pcraster import *


from osgeo import gdal
from osgeo import osr
import os, sys


class ConvertMapsToNetCDF4():
    def __init__(self, attribute=None):


        # latitudes and longitudes
        reso = 1000.0
        reso2 = reso/2.0
        lat1 = 2340000.0 - reso2
        lon1 = 3150000 + reso2

        self.yy = np.arange(lat1, 1970000, -reso)
        self.xx = np.arange(lon1, 3680000.0, reso)


        # netCDF format and attributes:
        self.format = 'NETCDF4_CLASSIC'
        self.attributeDictionary = {}
        if attribute == None:
            self.attributeDictionary['institution'] = "IIASA"
            self.attributeDictionary['title'] = "LDD"
            self.attributeDictionary['description'] = 'river network map based on EU-DEM and Eilander et al. 2021'
        else:
            self.attributeDictionary = attribute


    def writeToNetCDF(self, ncFileName, varShortNames, varLongNames, varUnits,  timeAttribute=None):
        rootgrp = Dataset(ncFileName, 'w', format=self.format)

        # general Attributes
        rootgrp.history = 'Created ' + timex.ctime(timex.time())
        rootgrp.Conventions = 'CF-1.6'
        rootgrp.Source_Software = 'Python netCDF4_Classic'
        #rootgrp.esri_pe_string = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.0174532925199433]]'
        #rootgrp.keywords = 'water fraction, Global'

        # -create dimensions - time is unlimited, others are fixed
        rootgrp.createDimension('y', len(self.yy))
        rootgrp.createDimension('x', len(self.xx))

        y = rootgrp.createVariable('y', 'f8', ('y',))
        y.long_name = 'y coordinate of projection'
        y.units = 'Meter'
        y.standard_name = 'y'
        y.axis = "Y"

        x = rootgrp.createVariable('x', 'f8', ('x',))
        x.long_name = 'x coordinate of projection'
        x.units = 'Meter'
        x.standard_name = 'x'
        x.axis = "X"

        y[:] = self.yy
        x[:] = self.xx

        if timeAttribute != None:
            # rootgrp.createDimension('time',None)
            no = 2010-1900
            rootgrp.createDimension('time', no)
            # every 10 days

            date_time = rootgrp.createVariable('time', 'f4', ('time',))
            date_time.standard_name = 'time'
            date_time.long_name = 'Days since 1901-01-01'
            date_time.units = 'Days since 1901-01-01'
            date_time.calendar = 'standard'
        else:
            pass

        for i in range(0, len(varShortNames)):
            shortVarName = varShortNames[i]
            if varLongNames != None:
                longVarName = varLongNames[i]
            else:
                longVarName = shortVarName
            if varUnits != None:
                # unitVar = varUnits[i]
                unitVar = varUnits
            else:
                unitVar = 'undefined'
            if timeAttribute != None:
                var = rootgrp.createVariable(shortVarName, 'f4', ('time', 'y', 'x',), fill_value=1e20, zlib=True)
            else:
                var = rootgrp.createVariable(shortVarName, 'f4', ('y', 'x',), fill_value=1e20, zlib=True)
            var.standard_name = shortVarName
            var.long_name = longVarName
            var.units = unitVar
            var.esri_pe_string = "PROJCS[\"ETRS_1989_LAEA\",GEOGCS[\"GCS_ETRS_1989\",DATUM[\"D_ETRS_1989\",SPHEROID[\"GRS_1980\",6378137.0,298.257222101]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Lambert_Azimuthal_Equal_Area\"],PARAMETER[\"false_easting\",4321000.0],PARAMETER[\"false_northing\",3210000.0],PARAMETER[\"central_meridian\",10.0],PARAMETER[\"latitude_of_origin\",52.0],UNIT[\"Meter\",1.0]]"

        attributeDictionary = self.attributeDictionary
        for k, v in attributeDictionary.items():
            setattr(rootgrp, k, v)

        rootgrp.sync()
        rootgrp.close()





# ------------------------------------
# ------------------------------------
# ------------------------------------

inDir = "P:/watmodel/CWATM/cwatm_input_1km_ebro/input_netcdf/routing/"

outDir = "P:/watmodel/CWATM/cwatm_input_1km_ebro/input_netcdf/routing/"
netcdfOut =outDir + "ldd2.nc"

inName = inDir+"ldd1.map"

varShortNames = ['ldd']
varLongNames = ['drainage network']
# We have to standardize units based on  the CF convention.
varUnits = '[-]'

newMap = ConvertMapsToNetCDF4(attribute=None)
newMap.writeToNetCDF(netcdfOut, varShortNames, varLongNames,  varUnits, timeAttribute=None)


startingDate = '1901-01-01'
date_units = 'Days since 1901-01-01'
date_calendar = 'standard'


# ------------------------------------
# ------------------------------------
# ------------------------------------


timedelta1 =[]
shortVarName = varShortNames[0]


# read from tif
nf2 = Dataset(netcdfOut, 'a')




ds = gdal.Open(inName)
cols = ds.RasterXSize
rows = ds.RasterYSize
value = np.array(ds.GetRasterBand(1).ReadAsArray())


#nf2.variables['time'][i] = date2num(timeStamp, date_units, date_calendar)
nf2.variables[shortVarName][:, :] = (value)


    # close dataset
ds = None

#i += 1

nf2.close()
print ("Done")


