# coding=utf-8
# @Time    : 4/12/2018 2:21 PM
# @Author  : Yanwen Wang

# This file aims to detect true craters from candidates by normalized profiles.

import os
import numpy as np
import time
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import datetime

Time = datetime.datetime.now()
Starttime = time.time()

# Read the positive train samples.
TrnSplsPOSFileName = (os.getcwd() + "/InputData/" +
                      "TrnSplsPOSProfiles_attr_set-2018-12-10.txt")
TrnSplsPOS = open(TrnSplsPOSFileName)
TrnSplsPOSPrfls = []
for line in TrnSplsPOS:
    # Split[2:-1] aims to remove the 1&2 column (row and col) and last column
    #  (line breaks). And then convert string to int.
    dataline = line.split(',')[:-1]
    dataline = [float(i) for i in dataline]
    TrnSplsPOSPrfls.append(dataline)
# Use TrnSplsPOSData to record the normalized positive profiles' shape.
TrnSplsPOSData = np.array(TrnSplsPOSPrfls)[:,5:]
# Initial TrnSplsPOSLabel for record the positive profiles as target label 1.
TrnSplsPOSLabel = np.ones((len(TrnSplsPOSPrfls)))

# Read the negative train samples.
TrnSplsNEGFileName = (os.getcwd() + "/InputData/" +
                      "TrnSplsNEGProfiles_attr_set-2018-12-10.txt")
TrnSplsNEG = open(TrnSplsNEGFileName)
TrnSplsNEGPrfls = []
for line in TrnSplsNEG:
    # Split[2:-1] aims to remove the 1&2 column (row and col) and last column
    #  (line breaks). And then convert string to int.
    dataline = line.split(',')[:-1]
    dataline = [float(i) for i in dataline]
    TrnSplsNEGPrfls.append(dataline)
# Use TrnSplsNEGData to record the normalized negative profiles' shape.
TrnSplsNEGData = np.array(TrnSplsNEGPrfls)[:,5:]
# Initial TrnSplsPOSLabel for record the negative profiles as target label 0.
TrnSplsNEGLabel = np.zeros((len(TrnSplsNEGPrfls)))

# Combine the positive and negative training samples.
TrainData = np.vstack((TrnSplsPOSData, TrnSplsNEGData))
TrainLabel = np.hstack((TrnSplsPOSLabel, TrnSplsNEGLabel))

# Build the random forest classifier.
clf = RandomForestClassifier(n_estimators=200, max_features=10,
                             bootstrap=True, n_jobs=1)
clf.fit(TrainData, TrainLabel)

# Read the profiles data of crater candidates in application area.
TstFileName = (os.getcwd() + "/InputData/" +
               "TstSplsProfiles_attr_set-2018-12-10.txt")
Tst = open(TstFileName)
TstPrfls = []
for line in Tst:
    # Split[2:-1] aims to remove the 1&2 column (row and col) and last column
    #  (line breaks). And then convert string to int.
    dataline = line.split(',')[:-1]
    dataline = [float(i) for i in dataline]
    TstPrfls.append(dataline)
# Use TstData to record the normalized negative profiles' shape.
TstData = np.array(TstPrfls)[:,5:]

# Classification of candidates' profiles by random forests.
TestResult = clf.predict(TstData)
TestProb = clf.predict_proba(TstData)

# Draw the classification result.
x = range(10)
for i in range(len(TstPrfls)):
    if TestResult[i] == 1:
        plt.plot(x, TstPrfls[i][5:15], color='g', alpha = 0.3)
    else:
        plt.plot(x, TstPrfls[i][5:15], color='r', alpha=0.3)
plt.show()

# Save the result by txt file.
fo = open(os.getcwd() + "/OutputData/" + 'TstProfiles_result' + str(
        Time.year) + "-" + str(Time.month) + "-" + str(Time.day) + '.txt', 'wb')
for i in range(len(TstPrfls)):
    for j in range(5):
        fo.write(str(TstPrfls[i][j]))
        fo.write(',')
    fo.write(str(TestResult[i])+',')
    fo.write(str(TestProb[i,1]) + ',')
    fo.write('\r\n')

Endtime = time.time()
calctime = Endtime - Starttime
print("The time of crater candidates profiles classification is " + str(
        calctime) + " s.")

print "OK"