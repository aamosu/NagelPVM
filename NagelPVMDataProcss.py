import serial
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import csv
import time

# Serial Port Init
SerPort = 'COM4'
BAUD_RATE = 115200
ser = serial.Serial(SerPort, BAUD_RATE)


# Clear serial input buffer
while ser.in_waiting > 0:
    ser.read()

# Close the serial port
ser.close()

# Wait for a short time to ensure the buffer is cleared
time.sleep(1)

# Reopen the serial port
ser = serial.Serial(SerPort, BAUD_RATE)

# Empty Arrays to store data
timeValsX = []
sensorValData = []
recordedTimeValsX = []
recordedSensorValData = []
prevRecordedTimeValsX = []  # Define previous session recorded time values
prevRecordedSensorValData = []  # Define previous session recorded sensor values

# Flag to control animation
running = False
capture = False
plot_enabled = False  # Flag to enable plotting after the first 10 valid readings

# Counter to keep track of valid readings greater than 1 second
valid_reading_count = 0

# CSV file to store captured data
capture_file = 'captured_data.csv'

# function to read in data from Arduino
def readProcessData():
    global plot_enabled
    global valid_reading_count
    
    line = ser.readline().decode('utf-8').strip()
    sensorValues = line.split(',')
    
    # Check if the line has the expected number of values
    if len(sensorValues) == 2:
        timeVal_str, sensorVal_str = sensorValues
        try:
            timeVal = float(timeVal_str)
            sensorVal = float(sensorVal_str)
            
            # Check if timeVal is greater than 1 second
            if timeVal > 1.0:
                valid_reading_count += 1
            
            # If we've received 10 valid readings greater than 1 second, enable plotting
            if valid_reading_count >= 10:
                plot_enabled = True
            
            # Append data only if plotting is enabled
            if plot_enabled:
                timeValsX.append(timeVal)
                sensorValData.append(sensorVal)
                if capture:
                    recordedTimeValsX.append(timeVal)
                    recordedSensorValData.append(sensorVal)
                    
        except ValueError:
            print("Invalid data format:", line)

# Function to update the CSV file with captured data
def updateCaptureFile():
    with open(capture_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Time', 'Pressure'])
        for time, pressure in zip(recordedTimeValsX, recordedSensorValData):
            writer.writerow([time, pressure])

def update_plot(frame):
    if running:
        readProcessData()
        ax.clear()
        ax.plot(timeValsX, sensorValData, label='All Data', color="blue")
        
        # Plot recorded data segments separately
        if recordedTimeValsX and capture:
            segment_start_idx = 0
            segment_complete = False  # Flag to indicate if the last segment was complete
            for i in range(1, len(recordedTimeValsX)):
                if recordedTimeValsX[i] - recordedTimeValsX[i-1] > 0.1:  # Adjust the threshold as needed
                    ax.axvspan(recordedTimeValsX[segment_start_idx], recordedTimeValsX[i], 
                            color="red", alpha=0.5)
                    segment_start_idx = i
                    segment_complete = True

            # Only plot the last segment if it was complete
            if segment_complete:
                ax.axvspan(recordedTimeValsX[segment_start_idx], recordedTimeValsX[-1], 
                        color="red", alpha=0.5)

# Function to save recorded data to a CSV file
def saveRecordedData(filename, timeVals, sensorVals):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Time', 'Pressure'])
        for time, pressure in zip(timeVals, sensorVals):
            writer.writerow([time, pressure])

def startRecordAnimation():
    global capture  
    capture = True

def stopRecordAnimation():
    global capture
    capture = False
    # Update the CSV file with captured data
    updateCaptureFile()

def startAnimation():
    global running
    running = True

def stopAnimation():
    global running
    running = False

def on_close():
    # Save recorded data to a CSV file
    saveRecordedData('PVMData.csv', timeValsX, sensorValData)
    # Close the serial port
    ser.close()
    # Destroy the tkinter window
    window.destroy()

# Create main window
window = tk.Tk()
window.title("Matplotlib in Tkinter")

# Create a Matplotlib figure and axis
fig = Figure(figsize=(8, 6))
ax = fig.add_subplot(111)

# Embed the plot into the Tkinter window
canvas = FigureCanvasTkAgg(fig, master=window)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

# Create start and stop buttons

start_button = tk.Button(window, text="START", command=startAnimation)
start_button.pack(side=tk.TOP)

stop_button = tk.Button(window, text="STOP", command=stopAnimation)
stop_button.pack(side=tk.TOP)

start_button = tk.Button(window, text="Record Start", command=startRecordAnimation)
start_button.pack(side=tk.TOP)

stop_button = tk.Button(window, text="Record Stop", command=stopRecordAnimation)
stop_button.pack(side=tk.TOP)

# Live Data Collection
ani = FuncAnimation(fig, update_plot, interval=10)

# Close event handler
window.protocol("WM_DELETE_WINDOW", on_close)

window.mainloop()
