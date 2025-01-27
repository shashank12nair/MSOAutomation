import socket
import csv
import time
import matplotlib.pyplot as plt
from datetime import datetime  # std library

# Oscilloscope connection details
oscilloscope_ip = "192.168.0.2"
oscilloscope_port = 4000  # Default port for SCPI commands over sockets

# Create a socket and connect to the oscilloscope
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((oscilloscope_ip, oscilloscope_port))

# Function to send a SCPI command and read the response
def send_scpi(command):
    sock.sendall((command + "\n").encode())  # Send command with newline
    response = sock.recv(4096).decode().strip()  # Receive and decode the response
    return response

# Enable measurement statistics (if not already enabled)
# send_scpi("MEASU:STAT ON")

# Define CSV file for logging
dt = datetime.now()  # Generate a filename based on the current Date & Time
data_file = dt.strftime("C:/Users/seema/PycharmProjects/MSOAutomation/data/amplitude_data_%Y%m%d_%H%M%S.csv")

# Data storage for plotting
times = []
amplitudes = []

# Open the CSV file for writing
with open(data_file, mode='w', newline='') as file:
    csv_writer = csv.writer(file)

    # Write the header row
    csv_writer.writerow(["Time (ms)", "Amplitude (V)"])

    # Define logging parameters
    sampling_interval = 0.1  # 10 ms
    logging_duration = 60  # 1 minute
    num_samples = int(logging_duration / sampling_interval)

    # Start logging
    start_time = time.time()
    for i in range(num_samples):
        # Query amplitude measurement from the oscilloscope
        amplitude = send_scpi("MEASU:MEAS1:VAL?")  # MEAS1 configured for Amplitude

        # Get the current time in milliseconds
        elapsed_time = (time.time() - start_time) * 1000

        # Store data for plotting
        times.append(round(elapsed_time, 1))
        amplitudes.append(float(amplitude))

        # Write data to the CSV file
        csv_writer.writerow([round(elapsed_time, 1), float(amplitude)])

        # Wait for the next sampling interval
        time.sleep(sampling_interval)

print(f"Data logging complete. File saved as '{data_file}'.")

# Close the socket connection
sock.close()

# # Plot the amplitude values against time
# plt.figure(figsize=(10, 6))
# plt.plot(times, amplitudes, label="Amplitude (V)", color="blue")
# plt.title("Amplitude vs Time")
# plt.xlabel("Time (ms)")
# plt.ylabel("Amplitude (V)")
# plt.grid(True)
# plt.legend()
# plt.tight_layout()
# plt.show()