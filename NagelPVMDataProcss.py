import serial
import matplotlib.pyplot as plt 
from matplotlib.animation import FuncAnimation
import csv 
import time 
import numpy as np
import sys

# Serial Port Init 

SerPort= 'COM4'
BAUD_RATE= 115200

ser= serial.Serial(SerPort,BAUD_RATE)


# Empty Arrays to store data 

timeValsX= []
sensorValData= []

dirrX=[]
dirrY=[]








#function to read in data from Arduino 

def readProcessData():
    line= ser.readline().decode('utf-8').strip()
    sensorValues= line.split(',')

    #add associated time values to sensor data
    try:
        #add associated time values to array 
        timeValsX.append(float(sensorValues[0]))
        #add Sensor Data to array
        sensorValData.append(float(sensorValues[1]))
    except:                                             # Pass if data point is bad                               
            pass

   # print(f'Time: {sensorValues[0]}, Pressure: {sensorValues[1]}')
    #print(sensorValData)


def adjust_values(array):
    adjusted_array = np.copy(array)

    for i in range(1, len(array)):
        percent_change = (array[i] - array[i-1]) / array[i-1] * 100

        if np.abs(percent_change) <= 10:
            adjusted_array[i] = adjusted_array[i-1]

    return adjusted_array

    

def update_plot(frame):

    readProcessData()
    plt.cla()
    plt.plot(timeValsX, sensorValData, label='Pressure')
    plt.xlabel('Time')
    plt.ylabel('Pressure')
    plt.legend()

    


def on_close(event):
    with open('PVMData.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Time', 'Pressure'])
        for x, s1 in zip(timeValsX, sensorValData):
            writer.writerow([x,s1])
    ser.close()
    pltDataFromcsv()
 

def pltDataFromcsv ():

    
    plt.subplot(2, 1, 1)
    plt.plot(timeValsX,sensorValData,label="Pressure vs Time")
    # plt.plot(timeValsX,sensorValData,marker="o", markersize=20, markeredgecolor="red", markerfacecolor="green")
    plt.xlabel('Time') 
    plt.ylabel('Pressure') 
    plt.title('Pressure vs Time', fontsize = 20) 
    plt.legend() 
    

    

    plt.subplot(2, 1, 2)
    plt.plot(timeValsX,adjust_values(sensorValData),label="Stabilized") 
    
    #sensorValData_np= np.array(sensorValData)
    timeValsX_np= np.array(timeValsX)
    dirrVal=np.diff(sensorValData)

    timeValsX_np = timeValsX_np[:len(dirrVal)]


    plt.plot(timeValsX_np,dirrVal, color="blue",label='Derivative')

    plt.grid() 
    plt.show()

   



def calculate_derivative(array):
    derivative = np.zeros_like(array, dtype=float)

    for i in range(1, len(array)):
        derivative[i] = (array[i] - array[i-1])

    return derivative
    

# Live Data Collection 
fig, axs = plt.subplots()
fig.canvas.mpl_connect('close_event', on_close)
ani= FuncAnimation(fig, update_plot,interval=10)
plt.rcParams["figure.figsize"] = (18, 10)
plt.show()

sys.exit()

