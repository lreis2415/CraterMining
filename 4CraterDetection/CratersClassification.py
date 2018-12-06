# coding=utf-8
# @Time    : /6/2018 6:43 PM
# @Author  : Yanwen Wang

# This file aims to show the result of crater detection.

import os
import numpy as np
import time
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

Starttime = time.time()

# Read the candidates profiles classification result.
fTestResultFileName = os.getcwd() + "/OutputData/" + 'TstProfiles_result.txt'
fTestResult = open(fTestResultFileName)
TestResultData = []
for line in fTestResult:
    dataline = line.split(',')[:-1]
    dataline = [float(i) for i in dataline]
    TestResultData.append(dataline)

CratersResult = []
ProfilesProbSum = 0
ProfilesNumSum = 0
# For the easy-coding of following loop.
TestResultData.append([0,0,0,0,0,0,0])
for i in range(len(TestResultData)-1):
    # The situation that next profiles belong to the same crater candidate as
    #  well.
    if TestResultData[i][2] == TestResultData[i+1][2] :
        # Add binary profile result. The sum is the IS-CRATER profiles' number.
        ProfilesProbSum = ProfilesProbSum + TestResultData[i][5]
        # Move to next profile in this crater candidate.
        ProfilesNumSum = ProfilesNumSum + 1
    # The situation that this profile is the final one of this crater candidate.
    else:
        # Add binary profile result. The sum is the IS-CRATER profiles' number.
        ProfilesProbSum = ProfilesProbSum + TestResultData[i][5]
        # Calculate the probability of this candidate can be classified as
        # crater.
        CraterProb = float(ProfilesProbSum/ProfilesNumSum)
        # If probability no less than 0.5, is crater; otherwise, is not.
        if CraterProb >= 0.5:
            HardRst = 1
        else:
            HardRst = 0
        # Record the result of candidate classification result.
        CratersResult.append([TestResultData[i][2], CraterProb, HardRst])
        ProfilesProbSum = 0
        ProfilesNumSum = 0

foFileName = os.getcwd() + "/OutputData/" + "CratersResult-Binary.txt"
fo = open(foFileName,'wb')
for i in range(len(CratersResult)):
    for j in range(len(CratersResult[i])):
        fo.write(str(CratersResult[i][j]))
        fo.write(',')
    fo.write('\r\n')

print "OK"