# coding=utf-8
# @Time    : 27/11/2018 10:29 PM
# @Author  : Yanwen Wang

# This file aims to detect the crater candidates pixels in application area.

# The positive samples are craters area delineated by experts. The negative
# samples are non-crater area.

import numpy as np
from pygeoc.raster import RasterUtilClass
import time
import datetime
from sklearn.ensemble import RandomForestClassifier
import os

StartTime = time.time()

# Read the training samples' labels.
# The pixels whose value is 1 are positive samples. The pixels whose value is
#  0 are negative samples.
TrainFileName = os.getcwd() + "/InputData/" + "Train_Craters.tif"
TrnSplsLbls = RasterUtilClass.read_raster(TrainFileName)
# The max scale (pixel as unit) of multiscale landforms is 60.
r = 60
# Convert to 1-d array for training.
TrnSplsLbls1D = TrnSplsLbls.data.reshape(TrnSplsLbls.nRows*TrnSplsLbls.nCols, 1)
# Read the training samples' input features which are multiscale landform
# elements.
# Initial the training landform elements data.
TrnSplsLE = np.zeros((TrnSplsLbls.nRows * TrnSplsLbls.nCols, r))
# Read the records from the txt file.
fTrnSplsLE = open(os.getcwd() + "/InputData/" + "TrainLE_1km_r60_500m.txt")
for line in fTrnSplsLE:
    # The 1st and 2nd number in the line are record's row number and
    # column number. The numbers in range [3, r] are landform elements. The
    # last character in a line is ',' for making an end, need to be ignored in
    # reading data.
    # The type of numbers from txt is str, need to be transformed into int.
    dataline = line.split(',')[:-1]
    dataline = [int(i) for i in dataline]
    index = (dataline[0])*(TrnSplsLbls.nCols) + (dataline[1])
    TrnSplsLE[index] = dataline
TrnSplsLE = TrnSplsLE[:, 2:r]

# Combine the labels TrnSplsLbls1D and input features TrnSplsLE and get the
# training samples.
TrnSpls = np.hstack((TrnSplsLE, TrnSplsLbls1D))

# Build a random forest classifier
clf = RandomForestClassifier(n_estimators=200, max_features=10,
                             bootstrap=True, n_jobs=1)
# Train this classifier.
TrnLabels = TrnSpls[:, -1:]
TrnInputfeatures = TrnSpls[:, :-1]
clf.fit(TrnInputfeatures, TrnLabels)
# Record the time of reading training samples and training classifier,
RFTime = time.time()
print("The time of reading training samples and training classifier is " +
      str(RFTime - StartTime) + " s.")

# Read the DEM of application(testing) area.
TstDEMFileName = os.getcwd() + "/InputData/" + "Test1DEM_500m_calc.tif"
TstDEM = RasterUtilClass.read_raster(TstDEMFileName)
# Read the multiscale landform elements of application area's samples.
TstSplsLE = np.zeros((TstDEM.nRows * TstDEM.nCols, r))
# Read the records from the txt file.
fTstSplsLE = open(os.getcwd() + "/InputData/" + "Test1LE_1km_r60_500m.txt")
for line in fTstSplsLE:
    dataline = line.split(',')[:-1]
    dataline = [int(i) for i in dataline]
    index = (dataline[0]) * (TstDEM.nCols) + (dataline[1])
    TstSplsLE[index] = dataline
TstSplsLE = TstSplsLE[:, 2:r]

# Detect the crater candidates in application area by random forest classifier.
TstRst = clf.predict(TstSplsLE)
TstProb = clf.predict_proba(TstSplsLE)

# Save the result as a image.
# Convert the 1-d result into 2-d result.
TstCrtCddts = np.zeros((TstDEM.nRows, TstDEM.nCols))
k = 0
for i in range(TstDEM.nRows):
    for j in range(TstDEM.nCols):
        TstCrtCddts[i, j] = TstRst[k]
        k = k+1
# Write the result into TIFF file.
Time = datetime.datetime.now()
ClcTstRstName = (os.getcwd() + "/OutputData/" + "CraterCandidatesPixels_" +
                 str(Time.year) + "-" + str(Time.month) + "-" + str(Time.day)
                 + ".tif")
RasterUtilClass.write_gtiff_file(ClcTstRstName, TstDEM.nRows, TstDEM.nCols,
                                 TstCrtCddts, TstDEM.geotrans, TstDEM.srs,
                                 32767, TstDEM.dataType)

# Record the time of detecting crater candidates.
FinishTime = time.time()
print("The time of detecting crater candidates is " +
      str(FinishTime - RFTime) + " s.")

print "OK"