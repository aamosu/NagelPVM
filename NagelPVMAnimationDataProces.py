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
spans = []  # List to store details of the last three spans
#selectedPressureSave=[]
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
line, = ax.plot([], [], 'r-')  # Initialize an empty line and use it for updating
ax.set_xlabel('Time')
ax.set_ylabel('Pressure')
canvas = FigureCanvasTkAgg(fig, master=window)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Function to read pressure data from a serial port
def read_process_data():
    global initial_discards,timeValsX,sensorValData
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
                print("Invalid:", line)

# Function to update the plot
def update_plot(frame):
    if running:
        read_process_data()
        line.set_data(timeValsX, sensorValData)
        ax.relim()  # Recompute the ax.dataLim
        ax.autoscale_view()  # Update axes limits
        canvas.draw_idle()  # Use draw_idle to redraw the plot

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
    if not running:
        running = True
        capture=True
        startRecordAnimation()
        ani.event_source.start()

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
        canvas.draw()
        enable_span_selector()

# Function to save recorded data to a CSV file
def saveRecordedData(filename, timeVals, sensorVals):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Time', 'Pressure'])
        for time, pressure in zip(timeVals, sensorVals):
            writer.writerow([time, pressure])

# Close event handler
def on_close():
    global spans
    if running and ani:
        ani.event_source.stop()
    if ser.is_open:
        ser.close()
    window.destroy()
    print(spans)

def enable_span_selector():
    
    def onselect(xmin, xmax):
        global spans
        if not running:  # Ensure that the spans are added only when not running
            indmin, indmax = np.searchsorted(timeValsX, (xmin, xmax))
            indmax = min(len(timeValsX) - 1, indmax)
            if indmin < indmax:
                selectedPressure = sensorValData[indmin:indmax]
                avgPressure = np.mean(selectedPressure) if selectedPressure else 0
                spans.append((xmin, xmax, avgPressure))
                if len(spans) > 3:
                    spans=spans[-3:]
                                # Clear old horizontal spans and redraw only the current valid ones
                for artist in ax.artists:
                    artist.remove()
                
                # Redraw all valid spans
                for span in spans:
                    s_xmin, s_xmax, _ = span
                    # Normalize span drawing based on the x-limits of the data
                    data_span_width = timeValsX[-1] - timeValsX[0] if timeValsX else 1
                    ax.axhspan(min(selectedPressure), max(selectedPressure), xmin=(s_xmin - timeValsX[0]) / data_span_width, 
                               xmax=(s_xmax - timeValsX[0]) / data_span_width, color='yellow', alpha=0.3)

                print(f"Average pressure between {timeValsX[indmin]}s and {timeValsX[indmax]}s: {avgPressure:.2f} atm")

    global span
    span = SpanSelector(ax, onselect, 'horizontal', useblit=True, props=dict(alpha=0.5, facecolor='red'))


def deleteOldAvg():
    global spans
    if spans:
        spans.pop()
        



# Buttons to control the live plot
start_button = tk.Button(window, text="Start", command=start_animation)
start_button.pack(side=tk.LEFT)

stop_button = tk.Button(window, text="Stop", command=stop_animation)
stop_button.pack(side=tk.LEFT)

stop_button = tk.Button(window, text="REDO", command= deleteOldAvg)
stop_button.pack(side=tk.LEFT)


# Live Data Collection
ani = FuncAnimation(fig, update_plot, interval=100)

window.protocol("WM_DELETE_WINDOW", on_close)
window.mainloop()






