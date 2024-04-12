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
#import pandas as pd

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
label_cycle = ['Pa', 'P0', 'Pk']  # Labels for the averages
current_label_index = 0  # Index to track which label to use next
running = False
capture=False 
ani = None
span = None

recordedAverages=[]

# Constants
R = 8.314  # Ideal gas constant in J/(mol*K)
T = 298.15  # Room temperature in Kelvin

# Global variable to store pressures and span data
pressures = {}


initial_discards = 20  # Number of initial readings to discard

# Tkinter GUI setup
window = tk.Tk()
window.title("Live Pressure Data")

fig = Figure(figsize=(8, 6))
ax = fig.add_subplot(111)
line, = ax.plot([], [], 'r-')  # Initialize an empty line and use it for updating
ax.set_xlabel('Time[s]')
ax.set_ylabel('Pressure[atm]')
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
        writer.writerow(['Time[s]', 'Pressure[atm]'])
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
    summary()

def enable_span_selector():
    global spans, current_label_index, label_cycle

    def onselect(xmin, xmax):
        global current_label_index
        global spans
        if not running:
            indmin, indmax = np.searchsorted(timeValsX, (xmin, xmax))
            indmax = min(len(timeValsX) - 1, indmax)
            if indmin < indmax:
                selectedPressure = sensorValData[indmin:indmax]
                avgPressure = np.mean(selectedPressure) if selectedPressure else 0
                label = label_cycle[current_label_index % 3]  # Get the current label
                spans.append((timeValsX[indmin], timeValsX[indmax], avgPressure, label))
                current_label_index += 1  # Move to the next label
                ax.axhspan(min(selectedPressure), max(selectedPressure), xmin=xmin/10, xmax=xmax/10, color='yellow', alpha=0.3)
                
                # Limit spans list to last 9 entries and cycle through labels
                if len(spans) > 9:
                    spans = spans[-9:]

    global span
    span = SpanSelector(ax, onselect, 'horizontal', useblit=True, props=dict(alpha=0.5, facecolor='red'))


def deleteOldAvg():
    global spans
    if spans:
        spans.pop()
        


def calculate_vk():
    """Calculate Vk using the pressures from the spans and user inputs for n1, nk."""
    try:
        n1 = float(entry_n1.get())
        nk = float(entry_nk.get())
        Vt = float(entry_VT.get())
        
        # Latest P0, Pa, Pk values
        P0 = pressures.get('P0')
        Pa = pressures.get('Pa')
        Pk = pressures.get('Pk')

        if None in (P0, Pa, Pk):
            result_label.config(text="Error")
            return


        Vk_eq1 = -nk * R * T + (n1 * R * T) / Pa
        Vk_eq2= ((P0 - Pk)/(Pa - Pk)) * Vt

        # Save to CSV
        current_time = time.strftime("%Y%m%d_%H%M%S")
        filename = f"Vk_Calculations_{current_time}.csv"
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['n1', 'nk', 'VT', 'P0', 'Pa', 'Pk', 'Vk_eq1', 'Vk_eq2'])
            writer.writerow([n1, nk, Vt, P0, Pa, Pk, Vk_eq1, Vk_eq2])


        result_label.config(text=f"Equation 1 Vk : {Vk_eq1:.2f} liters, Equation 2 Vk: {Vk_eq2:.2f} liters")
        
    except ValueError as e:
        result_label.config(text=f"Error: {e}")


def summary():

    summary_window = tk.Tk()
    summary_window.title("Span Summary and Calculation")

    # Display pressures and provide input fields for n1, nk, VT
    global entry_n1, entry_nk, entry_VT, result_label

    tk.Label(summary_window, text="n1 (moles):").pack()
    entry_n1 = tk.Entry(summary_window)
    entry_n1.pack()

    tk.Label(summary_window, text="nk (moles):").pack()
    entry_nk = tk.Entry(summary_window)
    entry_nk.pack()

    tk.Label(summary_window, text="VT (L):").pack()
    entry_VT = tk.Entry(summary_window)
    entry_VT.pack()

    tk.Label(summary_window, text="V1 (L):").pack()
    entry_VT = tk.Entry(summary_window)
    entry_VT.pack()

    calc_button = tk.Button(summary_window, text="Calculate Vk", command=calculate_vk)
    calc_button.pack()

    result_label = tk.Label(summary_window, text="")
    result_label.pack()

    # Prepare the span summary
    summary_text = "Span Summary:\n\n"
    summary_text += f"{'Index':<10}{'t1':<20}{'t2':<20}{'Pressure Label':<15}{'Avg Pressure':<15}\n"
    summary_text += "-" * 70 + "\n"

    for index, (t1, t2, avgPressure, label) in enumerate(spans):
        summary_text += f"{index+1:<10}{t1:<20.2f}{t2:<20.2f}{label:<15}{avgPressure:<15.2f}\n"
        pressures[label] = avgPressure  # Store last pressures with labels for calculation
    
    text = tk.Text(summary_window, height=20, width=100)
    text.insert(tk.END, summary_text)
    text.config(state='disabled')
    text.pack()

    summary_window.mainloop()




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






