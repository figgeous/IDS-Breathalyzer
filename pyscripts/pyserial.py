# Connection to Arduino and data collection
import time

import serial

ser = serial.Serial("COM7", 9600)
time.sleep(2)
# Loop that runs for five seconds while data is collected. Decode and remove whitespace
data = []
for i in range(0, 50):
    # Read data from serial port
    data.append(ser.readline().decode().strip())
    # Wait for 0.1 seconds
    time.sleep(0.1)
# Close serial port
ser.close()
# Print data
print(data)

# Plot the data with matplotlib
import matplotlib.pyplot as plt
import numpy as np

# Convert data to float
data = [float(i) for i in data]
# Plot the data
plt.plot(data)
# Set the x axis label
plt.xlabel("Time")
# Set the y axis label
plt.ylabel("Voltage")
# Set the title
plt.title("Voltage vs Time")
# Display the plot
plt.show()
