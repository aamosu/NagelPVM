import serial
import matplotlib.pyplot as plt 
from matplotlib.animation import FuncAnimation
import csv 
import time 

# Serial Port Init 

SerPort= 'COM4'
BAUD_RATE= 115200

ser= serial.Serial(SerPort,BAUD_RATE)


# Empty Arrays to store data 

timeValsX= []
sensorValData= []






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
    #timeValsX_new= []
    #sensorValData_new= []

    #timeValsX_new,sensorValData_new=deleteElements(timeValsX,sensorValData)
    plt.plot(timeValsX,sensorValData,label="Pressure vs Time")
    plt.plot(timeValsX[detect_slope_change(sensorValData)],sensorValData[detect_slope_change(sensorValData)],marker="o", markersize=20, markeredgecolor="red", markerfacecolor="green")
    plt.xlabel('Time') 
    plt.ylabel('Pressure') 
    plt.title('Pressure vs Time', fontsize = 20) 
    plt.grid() 
    plt.legend() 
    plt.show()

  


def detect_slope_change(arr):
    n = len(arr)

    # Calculate the slope between consecutive elements
    slopes = [arr[i + 1] - arr[i] for i in range(n - 1)]

    # Find the index where the slope significantly decreases
    for i in range(1, n - 1):
        if slopes[i] < slopes[i - 1]:
            return i
        
def deleteElements(array1, array2):
    # Find indexes of elements less than 0.5 in array1
    delete_indexes = [i for i in range(len(array1)) if array1[i] < 0.5]

    # Delete elements less than 0.5 in array1
    array1 = [element for element in array1 if element >= 0.5]

    # Delete corresponding elements at the same index in array2
    array2 = [array2[i] for i in range(len(array2)) if i not in delete_indexes]

    return array1, array2

'''
def detect_slope_change(data):
    # Calculate the slope between consecutive points
    slopes = [data[i] - data[i - 1] for i in range(1, len(data))]

    # Find the index where the slope significantly decreases
    for i in range(1, len(slopes)):
        if slopes[i] < 0.5 * slopes[i - 1]:  # Adjust the threshold as needed
            return i

    # If no significant slope change is found
    return -1
'''

# Live Data Collection 
fig, axs = plt.subplots()
fig.canvas.mpl_connect('close_event', on_close)
ani= FuncAnimation(fig, update_plot,interval=10)
plt.show()


