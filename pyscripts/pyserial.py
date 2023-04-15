# Connection to Arduino and data collection
import time

import serial

def get_potentiometer_values() -> float:
    """
    Connects to the serial port and collects data for 5 seconds
    """
    # Connect to serial port
    serial_port_name = "COM7"
    ser = serial.Serial(serial_port_name, 9600)
    # time.sleep(2)
    # Loop that runs for five seconds while data is collected. Decode and remove whitespace
    data = []
    for i in range(0, 50):
        # Read data from serial port
        data.append(float(ser.readline().decode().strip()))
        # Wait for 0.1 seconds
        time.sleep(0.1)
    # Close serial port
    ser.close()

    maximum_possible_potentio_value = 4095
    maximum_possible_bac = 0.3 # 0.3% BAC, which is close to comatosed
    maximum_measured = max(data)
    conversion_to_bac = (maximum_possible_bac / maximum_possible_potentio_value) * maximum_measured
    return conversion_to_bac
