# coding=utf-8
# @Time    : 4/12/2018 4:59 PM
# @Author  : Yanwen Wang

# This file aims to get the raster result of profiles classification.

import os
import numpy as np
import time
import shapefile
from pygeoc.raster import RasterUtilClass
import math
import matplotlib.pyplot as plt

# Define θ=0, π/2, π, 3π/2 line. These four line are skeleton of the lines set.
#          [0, 1]
#  [-1, 0]         [1, 0]
#          [0, -1]
skl_lines = [[0, 1], [1, 0], [0, -1], [-1, 0]]
# Theta is angle between line and x axis.
line_theta = [math.pi/6, math.pi/3, 2*math.pi/3, 5*math.pi/6, 7*math.pi/6,
              4*math.pi/3, 5*math.pi/3, 11*math.pi/6]


centersFileName = (os.getcwd() + "/InputData/" +
                   "CraterCandidatesObjects_centres")
centers = shapefile.Reader(centersFileName)
centers_records = centers.records()
# centers_info saves centers' rows and cols, IDs, radiuses(pixels).
centers_info = []
for i in range(len(centers_records)):
    temp_centers = centers_records[i]
    centers_info.append([temp_centers[6], temp_centers[7], temp_centers[1],
                         temp_centers[3]])

# Get the raster information (rows, columns, projections and others) from DEM.
DEMFileName = os.getcwd() + "/InputData/" + "Test1DEM_500m_calc.tif"
DEM = RasterUtilClass.read_raster(DEMFileName)
DEMdata = DEM.data

# Read the crater candidates' profiles' classification results.
fTestResultFileName = (os.getcwd() + "/OutputData/" + "TstProfiles_result.txt")
fTestResult = open(fTestResultFileName)
TestResultData = []
for line in fTestResult:
    dataline = line.split(',')[:-1]
    dataline = [float(i) for i in dataline]
    TestResultData.append(dataline)

# Initial the probability result of profiles' classification.
OutProfilesProb = np.zeros((DEM.nRows, DEM.nCols))
# Initial the binary result of profiles' classification.
OutProfiles = np.zeros((DEM.nRows, DEM.nCols))

# Draw the profiles
for i in range(len(TestResultData)):
    CenterRow = int(TestResultData[i][0])
    CenterCol = int(TestResultData[i][1])
    r = int(TestResultData[i][3])
    LineNum = int(TestResultData[i][4])
    # IsCrater is the index of profile's result. 1 means is crater profile.
    # And 0 means is not.
    IsCrater = TestResultData[i][5]
    Prob = float(TestResultData[i][6])
    # First draw the skeleton lines.
    if LineNum <4 : # skl_lines
        for k in range(1,r+1):
            temppoint = [CenterRow + k * skl_lines[LineNum][0], CenterCol + k
                         * skl_lines[LineNum][1]]
            OutProfiles[temppoint[0],temppoint[1]] = IsCrater
            OutProfilesProb[temppoint[0],temppoint[1]] = float(Prob)
    # Then draw other lines.
    else:
        LineNum = LineNum - 4
        theta = line_theta[LineNum]
        for k in range(1,r+1):
            temppoint = [CenterRow + int(k * math.sin(theta)),
                         CenterCol + int(k * math.cos(theta))]
            OutProfiles[temppoint[0], temppoint[1]] = IsCrater
            OutProfilesProb[temppoint[0], temppoint[1]] = float(Prob)

TstPrflsRstFileName1 = (os.getcwd() + "/OutputData/" + "TstPrflsRst_binary.tif")
RasterUtilClass.write_gtiff_file(TstPrflsRstFileName1, DEM.nRows,
                                 DEM.nCols, OutProfiles,
                                 DEM.geotrans, DEM.srs, 32767,
                                 DEM.dataType)

TstPrflsRstFileName2 = (os.getcwd() + "/OutputData/" +
                       "TstPrflsRst_probability.tif")
RasterUtilClass.write_gtiff_file(TstPrflsRstFileName2, DEM.nRows,
                                 DEM.nCols, OutProfilesProb,
                                 DEM.geotrans, DEM.srs, 32767,
                                 DEM.dataType)

print "OK"