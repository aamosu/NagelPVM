import serial
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import SpanSelector
from matplotlib.animation import FuncAnimation
import time
import csv

# Serial port configuration
SerPort = 'COM4'
BAUD_RATE = 115200
ser = serial.Serial(SerPort, BAUD_RATE)

# Global variables for plot data
timeValsX = []
sensorValData = []
recordedTimeValsX = []
recordedSensorValData = []
running = False
capture=False 
ani = None
span = None

initial_discards = 20  # Number of initial readings to discard
# Tkinter GUI setup
window = tk.Tk()
window.title("Live Pressure Data")

fig = Figure(figsize=(8, 6))
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=window)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Function to read pressure data from a serial port
def read_process_data():
    global initial_discards
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        sensorValues = line.split(',')
        if len(sensorValues) == 2:
            try:
                timeVal = float(sensorValues[0])
                sensorVal = float(sensorValues[1])
                if initial_discards > 0:
                    initial_discards -= 1  # Decrement the discard counter
                else:
                    timeValsX.append(timeVal)
                    sensorValData.append(sensorVal)
                    if capture:
                        recordedTimeValsX.append(timeVal)
                        recordedSensorValData.append(sensorVal)
            except ValueError:
                print("Invalid data format:", line)

# Function to update the plot
def update_plot(frame):
    if running:
        read_process_data()
        if timeValsX and sensorValData:
            ax.clear()
            ax.step(timeValsX, sensorValData, where='post', linestyle='--', color='r', label='Pressure')
            ax.set_xlabel('Time')
            ax.set_ylabel('Pressure')
            ax.set_title('Pressure-Time History')
            ax.set_ylim(0, max(sensorValData) + 1)
            ax.legend()
            ax.grid(True)
            canvas.draw()

def startRecordAnimation():
    global capture,ani 
    
    # Clear recorded data arrays
    if capture:
    #capture=True 
        del recordedTimeValsX[:]
        del recordedSensorValData[:]

    

# Function to start the animation
def start_animation():
    global running,capture,ani 
    running = True
    capture=True
    startRecordAnimation()
    ani.event_source.start()
    print(running)

def stopRecordAnimation():
    global capture
    capture = False

     # Start a new CSV file for this capture session
    current_time = time.strftime("%Y%m%d_%H%M%S")
    filename = f"capture_{current_time}.csv"
    saveRecordedData(filename, recordedTimeValsX, recordedSensorValData)

# Function to stop the animation and enable the SpanSelector
def stop_animation():
    global running,capture,ani,span 
    if running:
        running = False
        capture= False 
        stopRecordAnimation()
        ani.event_source.stop()
        #ani.event_source.start()
        #canvas.draw()
        #enable_span_selector()
    print(running)

# Function to save recorded data to a CSV file
def saveRecordedData(filename, timeVals, sensorVals):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Time', 'Pressure'])
        for time, pressure in zip(timeVals, sensorVals):
            writer.writerow([time, pressure])

# Close event handler
def on_close():
    if running and ani:
        ani.event_source.stop()
    if ser.is_open:
        ser.close()
    window.destroy()

def enable_span_selector():
    # Function to calculate and print the average pressure in the selected range
    def onselect(xmin, xmax):
        indmin, indmax = np.searchsorted(timeValsX, (xmin, xmax))
        indmax = min(len(timeValsX) - 1, indmax)
        if indmin < indmax:
            selected_pressure = sensorValData[indmin:indmax]
            if selected_pressure:
                average_pressure = np.mean(selected_pressure)
                print(f"Average pressure between {timeValsX[indmin]}s and {timeValsX[indmax]}s: {average_pressure:.2f} atm")
    
    span=SpanSelector(ax, onselect, 'horizontal', useblit=True, props=dict(alpha=0.5, facecolor='red'))




# Buttons to control the live plot
start_button = tk.Button(window, text="Start", command=start_animation)
start_button.pack(side=tk.LEFT)

stop_button = tk.Button(window, text="Stop", command=stop_animation)
stop_button.pack(side=tk.LEFT)


# Live Data Collection
ani = FuncAnimation(fig, update_plot, interval=100)

window.protocol("WM_DELETE_WINDOW", on_close)
window.mainloop()






