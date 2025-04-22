from helper_functions import *

import csv
import time


def get_amplitude_data(measNum, min = 1):

    dt = datetime.now()  # Generate a filename based on the current Date & Time
    fileName = dt.strftime("C:/Users/seema/PycharmProjects/MSOAutomation/data/amplitude_data_%Y%m%d_%H%M%S.csv")

    with open(fileName,mode="w",newline="") as file:
        csv_writer = csv.writer(file)

        csv_writer.writerow(["Time(ms)", "Amplitude(V)"]) # todo: need to check what the unit of amplitude will be

        rate = 0.1
        num_samples = int((min * 60) / rate)
        for i in range(num_samples):
            amplitude = query("MEASU:MEAS"+str(measNum)+":VAL?")

            csv_writer.writerow([rate * num_samples, float(amplitude)])

            time.sleep(rate)

        print("Data stored in the csv file.\r\n")

def main():

    format_input = input("Choose file format:\n  1. internal\n  2. spreadsheet\nEnter choice (1 or 2): ").strip()
    if format_input == "1":
        format_choice = "internal"
    elif format_input == "2":
        format_choice = "spreadsheet"
    else:
        print("Invalid choice. Defaulting to 'internal'.")
        format_choice = "internal"

    try:
        series_number = int(input("Enter series number (e.g., 1, 2, 3...): ").strip())
    except ValueError:
        print("Invalid series number. Defaulting to 1.")
        series_number = 1

    # Get wait time
    try:
        wait_time = float(input("Enter acquisition duration in seconds: ").strip())
    except ValueError:
        print("Invalid time. Defaulting to 10 seconds.")
        wait_time = 10.0

    # Start waveform saving
    save_waveforms_on_trigger(format_choice, series_number)

    # Wait for specified duration
    print(f"Waiting for {wait_time} seconds while acquisition runs...")
    time.sleep(wait_time)

    # Stop acquisition
    stop_waveform_saving()

    time.sleep(0.5)

    # Retrieve waveform files
    filename_pattern = f"TriggerEventWaveform_{format_choice}_{series_number}"
    retrieve_waveforms(filename_pattern)



if __name__ == "__main__":
    main()
    end()