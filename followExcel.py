import pandas as pd
import time
import os
from changeTemp import serialCom

class FollowExcel:
    # initialize class variables
    def __init__(self, serialPort, baud, file):
        self.serialPort = serialPort
        self.baud = baud
        self.file = file
        self.time = 0
        self.maxTime = 1
        self.temp = 48
        self.sc = serialCom(serialPort = self.serialPort, baud = self.baud)
        self.sc.changeTemp(self.temp)
        
    # method that starts following a csv file and matching the temperature and time data
    def start(self):
        #flag tells the program whether to continue or not
        global flag
        flag = False
        colTime = 'R1'
        colTemp = 'R2'
        # read the file variable's path to get name
        fileName = os.path.join(os.path.dirname(__file__), self.file)

        frame = pd.read_csv(fileName)
        # gets a list of all the time data and temp data in the same order
        timeData = pd.to_numeric(frame[colTime], errors='coerce').fillna(method='bfill').tolist()
        tempData = pd.to_numeric(frame[colTemp], errors='coerce').fillna(method='bfill').tolist()
        # last time in the list should be the largest time value
        self.maxTime = round(timeData[-1])
        startTime = time.time()

        # go throug the list indexs except for the lst one
        for i in range(len(timeData) - 1):
            if flag == True:
                return
            # change temperature to reflect the data
            self.sc.changeTemp(round(tempData[i]))
            self.sc.printInfo()
            self.time = round(timeData[i])
            self.temp = round(tempData[i])
            print("Time: " + str(round(timeData[i])))
            print()
            while(True):
                programTime = time.time() - startTime
                if programTime > self.time:
                    break
                if flag == True:
                    return
        # do the last index seperately
        self.sc.changeTemp(round(tempData[-1]))
        self.time = round(timeData[-1])
        self.temp = round(tempData[-1])
        self.sc.printInfo()
        print("Time: " + str(round(timeData[-1])))
        print()

    def stop(self):
        global flag
        flag = True # turns flag true which returns the start method, ending it