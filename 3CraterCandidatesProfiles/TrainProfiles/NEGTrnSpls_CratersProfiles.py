# coding=utf-8
# @Time    : 4/12/2018 10:14 AM
# @Author  : Yanwen Wang

# This file aims to obtain the normalized elevation profiles for negative
# training samples of non-craters area delineated by experts.

import os
import shapefile
from pygeoc.raster import RasterUtilClass
import numpy as np
import math
import matplotlib as mpl
import matplotlib.pyplot as plt
import time
import random
import datetime

Starttime = time.time()

# Define the profiles of craters.
# Define θ=0, π/2, π, 3π/2 line. These four line are skeleton of the lines set.
#          [0, 1]
#  [-1, 0]         [1, 0]
#          [0, -1]
skl_lines = [[0, 1], [1, 0], [0, -1], [-1, 0]]
# Theta is angle between line and x axis.
line_theta = [math.pi/6, math.pi/3, 2*math.pi/3, 5*math.pi/6, 7*math.pi/6,
              4*math.pi/3, 5*math.pi/3, 11*math.pi/6]


# Define the function of calculating the normalized elevation profiles.
# Input are the initial line data, center's elevation, center's coordinate
# and the ID of this line.
def calc_attributes(line_j, center_elev, center, line_ID):
    # The number of pixels in this line.
    points_num = len(line_j)
    # How many pixels should be averaged.
    long = float(points_num/10)
    # Initial the attr_set to save un-normalized 10-units profile line.
    attr_set = []
    # Get each unit's (averaged pixels') relative-elevation.
    for k in range(10):
        k_elev_sum = sum([k_elev for k_elev in line_j[int(k*long):int((k+1)*long)]])
        k_elev_num = len(line_j[int(k*long):int((k+1)*long)])
        k_attr = float(k_elev_sum/k_elev_num) - center_elev
        attr_set.append(k_attr)
    # Do normalization and store the normalized profile line.
    min_attr = min(attr_set)
    attr_range = max(attr_set) - min_attr
    std_attr_set = []
    # std_attr_set save the information of this crater's center. There are 4
    # parameters. 1st is row number. 2nd is column number. 3rd is crater
    # candidates' ID (column: grid_code). 4th is the pixels number of radius.
    for i in range(4):
        std_attr_set.append(center[i])
    # Add this line's ID of this crater candidates in std_attr_str.
    std_attr_set.append(line_ID)
    # Add the normalized line data in std_attr_str.
    for k in range(len(attr_set)):
        std_attr = float((attr_set[k] - min_attr)/attr_range)
        std_attr_set.append(std_attr)
    return std_attr_set


# Main function.
# Read the crater candidates centers' data.
CentersFileName = (os.getcwd() + "/InputData/" +
                   "TrainSamples_CratersCenters")
Centers = shapefile.Reader(CentersFileName)
CentersRcds = Centers.records()
# CentersInf saves centers' information. 1st is row number. 2nd is column
# number. 3rd is crater candidates' ID (column: grid_code). 4th is the pixels
#  number of radius.
CentersInf = []
for i in range(len(CentersRcds)):
    temp_centers = CentersRcds[i]
    CentersInf.append([temp_centers[6], temp_centers[7], temp_centers[1],
                         temp_centers[3]])

# Random select (corresponding train samples) circles from no craters area in
#  training area.
NoCratersFileName = os.getcwd() + "/InputData/" + "Train_NoCraters.tif"
NoCraters = RasterUtilClass.read_raster(NoCratersFileName)
# Restore the random circles' centers.
NoCratersCenters = []
for i in range(len(CentersInf)):
    x, y = np.where(NoCraters.data == CentersInf[i][3])
    k = random.randint(0, len(x))
    NoCratersCenters.append([x[k], y[k], CentersInf[i][2], CentersInf[i][3]])

# Read the DEM for elevation profiles' calculation.
DEMFileName = (os.getcwd() + "/InputData/" +
               "TrainDEM_500m_calc.tif")
DEM = RasterUtilClass.read_raster(DEMFileName)
DEMData = DEM.data

# Start the calculation of negative samples' profiles.
lines_attr_set = []
for i in range(len(NoCratersCenters)):
    center_i = NoCratersCenters[i]
    center_i_elev = DEMData[center_i[0],center_i[1]]
    i_r = center_i[3]
    i_ID = center_i[2]
    # Skeleton lines.
    for j in range(4):
        line_j_endpoint = [center_i[0] + i_r * skl_lines[j][0], center_i[1] +
                           i_r * skl_lines[j][1]]
        line_j = []
        # If this line is not out of the spatial range, this line will be
        # calculated.
        if (line_j_endpoint[0]>=0 and line_j_endpoint[0]<DEM.nRows and
            line_j_endpoint[1]>=0 and line_j_endpoint[1]<DEM.nCols) :
            # Extract the
            for k in range(1,i_r+1):
                line_j_temppoint =  [center_i[0] + k * skl_lines[j][0],
                                     center_i[1] + k * skl_lines[j][1]]
                line_j_temppoint_elve = DEMData[line_j_temppoint[0],
                                                line_j_temppoint[1]]
                line_j.append(line_j_temppoint_elve)
            line_j_attr = calc_attributes(line_j, center_i_elev, center_i, j)
            lines_attr_set.append(line_j_attr)
    # Given lines.
    for j in range(len(line_theta)):
        theta = line_theta[j]
        line_j_endpoint = [center_i[0] + int(i_r * math.sin(theta)),
                           center_i[1] + int(i_r * math.cos(theta))]
        line_j = []
        # If this line is not out of the spatial range, this line will be
        # calculated.
        if (line_j_endpoint[0]>=0 and line_j_endpoint[0]<DEM.nRows and
            line_j_endpoint[1]>=0 and line_j_endpoint[1]<DEM.nCols) :
            for k in range(1,i_r+1):
                line_j_temppoint = [center_i[0] + int(k * math.sin(theta)),
                                    center_i[1] + int(k * math.cos(theta))]
                line_j_temppoint_elve = DEMData[line_j_temppoint[0],
                                                line_j_temppoint[1]]
                line_j.append(line_j_temppoint_elve)
            line_j_attr = calc_attributes(line_j, center_i_elev, center_i, j+4)
            lines_attr_set.append(line_j_attr)
# Draw the lines.
x = range(10)
for i in range(len(lines_attr_set)):
    plt.plot(x, lines_attr_set[i][5:15], color='b', alpha = 0.3)
plt.show()

# Save the result in txt file.
TxtFileName = (os.getcwd() + "/OutputData/" + "TrnSplsNEGProfiles_attr_set" +
               ".txt")
fo = open(TxtFileName,'wb')
for i in range(len(lines_attr_set)):
    for j in range(len(lines_attr_set[i])):
        fo.write(str(lines_attr_set[i][j]))
        fo.write(',')
    fo.write('\r\n')

Endtime = time.time()
calctime = Endtime - Starttime
print("The time of negative training profile calculation is " + str(calctime)
      + " s.")

print "OK"