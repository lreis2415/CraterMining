# coding=utf-8
# @Time    : 27/11/2018 11:42 AM
# @Author  : Yanwen Wang

# This file aims to transform the crater candidates pixels detected by 1step
# to crater candidates objects.

# 1st, Do the opening for remove noise pixels. 2nd. Do the DBSCAN clustering
#  for distinguish different candidates and convert candidates pixels to
# candidates objects.
from pygeoc.raster import RasterUtilClass
import numpy as np
from sklearn.cluster import DBSCAN
import os
import datetime
import time

StartTime = time.time()

# Read the initial craters data.
InitCrtsFileName = ( os.getcwd() + "/InputData/" +
                     "CraterCndidatesPixels_2018-11-27.tif" )

InitCrts = RasterUtilClass.read_raster(InitCrtsFileName)

# Do the opening for remove noise pixels.
OpnCrtsData = RasterUtilClass.openning(InitCrtsFileName,1)
Time = datetime.datetime.now()
OpnCrtsFileName = (os.getcwd() + "/OutputData/" +
                   "CraterCandidatesPixelsOpenning_" + str(Time.year) + "-" +
                   str(Time.month) + "-" + str(Time.day) + ".tif")
RasterUtilClass.write_gtiff_file(OpnCrtsFileName, InitCrts.nRows,
                                 InitCrts.nCols, OpnCrtsData, InitCrts.geotrans,
                                 InitCrts.srs, 32767, InitCrts.dataType)

# Record the time of opening,
OpnTime = time.time()
print("The time of opening is " + str(OpnTime - StartTime) + " s.")

# Do the DBSCAN for distinguish each crater candidates.
# Get the coordinates of crater candidates' pixels after openning.
OpnCrtsPxls = np.where(OpnCrtsData == 1, 1, OpnCrtsData)
PxlsCoord = np.where(OpnCrtsPxls == 1)
PxlsCoord = np.array([PxlsCoord[0], PxlsCoord[1]]).swapaxes(0,1)
# Set the parameters of DBSCAN
eps = 2
min_samples = 10
# Run DBSCAN clustering.
DbScan = DBSCAN(eps=eps, min_samples=min_samples).fit(PxlsCoord)
# Get the 1-d DBSCAN labels for each pixel.
DbCrtsLbls = np.array(DbScan.labels_).reshape((DbScan.labels_.shape[0],1))
# Connect the pixels' coordinates and labels.
DbCrtsPxls = np.concatenate((PxlsCoord, DbCrtsLbls), axis=1)
# Output the result of DBSCAN clustering.
DbCrtsData = np.ones((InitCrts.nRows, InitCrts.nCols)) * 32767
for i in range(DbCrtsPxls.shape[0]):
    DbCrtsData[DbCrtsPxls[i,0], DbCrtsPxls[i,1]] = DbCrtsPxls[i,2]
OpnCrtsFileName =  (os.getcwd() + "/OutputData/" +
                    "CraterCandidatesPixelsDBSCAN_" + str(Time.year) + "-" +
                    str(Time.month) + "-" + str(Time.day) + ".tif")
RasterUtilClass.write_gtiff_file(OpnCrtsFileName, InitCrts.nRows,
                                 InitCrts.nCols, DbCrtsData, InitCrts.geotrans,
                                 InitCrts.srs, 32767, InitCrts.dataType)

# Record the time of DBSCAN,
DBScTime = time.time()
print("The time of DBScan is " + str(DBScTime - OpnTime) + " s.")

print "OK"
