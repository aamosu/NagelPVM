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

    #add associated time values to array 
    timeValsX.append(float(sensorValues[0]))
    #add Sensor Data to array
    sensorValData.append(float(sensorValues[1]))

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

fig, axs = plt.subplots()

fig.canvas.mpl_connect('close_event', on_close)

ani= FuncAnimation(fig, update_plot,interval=10)
plt.show()

