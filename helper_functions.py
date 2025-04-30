import time

from mso_comm import *

from datetime import datetime  # std library
from pathlib import Path
# import pandas as pd

# For tcpip and usb comm. based on pyvisa
def write(command):
    try:
        ret = scope.write(command)
        return ret
    except:
        print("Write operation failed.Try again.\r\n")
        return


def query(command):
    try:
        ret = scope.query(command)
        return ret
    except:
        print("Query operation failed.Try again.\r\n")
        return


def read_raw(size):
    try:
        ret = scope.read_raw(size)
        return ret
    except:
        print("Query operation failed.Try again.\r\n")
        return


def capture_image():
    write('SAVE:IMAGe \"C:/Temp.png\"')    # Save image to instrument's local disk

    dt = datetime.now()    # Generate a filename based on the current Date & Time
    fileName = dt.strftime("D:/pythonProjects/MSOAutomation/Images/IMG_%Y%m%d_%H%M%S.png")

    query('*OPC?')# Wait for instrument to finish writing image to disk

    write('FILESystem:READFile \"C:/Temp.png\"') # Read image file from instrument
    imgData = read_raw(1024 * 1024)

    file = open(fileName, "wb")  # Save image data to local disk
    file.write(imgData)
    file.close()

    write('FILESystem:DELEte \"C:/Temp.png\"') # Image data has been transferred to PC and saved. Delete image file from instrument's hard disk.
    print("Image captured successfully\r\n")


def transfer_file(src_path, dstn_path, delete_file = True):
    dt = datetime.now()  # Generate a filename based on the current Date & Time
    fileName = dt.strftime(str(dstn_path) + str(Path(src_path).name))


    write('FILESystem:READFile \"' + str(src_path) + "\"") # Read image file from instrument
    imgData = read_raw(1024 * 1024)

    file = open(fileName, "wb")  # Save image data to local disk
    file.write(imgData)
    file.close()
    query('*OPC?')

    # with open(fileName, "r") as file:
    #     lines = file.readlines()
    #
    # # Identify the row where "Labels" appears
    # data_start_row = next((i for i, line in enumerate(lines) if "Labels" in line), None)
    #
    # # Identify the actual data start row (row after labels)
    # data_start_row += 2  # The actual data starts two rows below "Labels"
    #
    # # Read the CSV using Pandas while keeping metadata
    # metadata = lines[:data_start_row]  # Preserve metadata
    # waveform_df = pd.read_csv(fileName, skiprows=data_start_row, header=None)
    #
    # # Assign column names dynamically using the row below "Labels"
    # column_names = lines[data_start_row - 1].strip().split(",")
    # waveform_df.columns = column_names
    #
    # # Convert to numeric values
    # waveform_df = waveform_df.apply(pd.to_numeric, errors='coerce')
    #
    # # Filter data between -80 ns to 80 ns
    # time_window = (waveform_df["TIME"] >= -80e-9) & (waveform_df["TIME"] <= 80e-9)
    # filtered_df = waveform_df[time_window]
    #
    # # Merge metadata with the filtered waveform data
    # final_csv_content = "".join(metadata) + filtered_df.to_csv(index=False, header=False)
    #
    # # Save final filtered file
    # with open(fileName, "w", newline='') as file:
    #     file.write(final_csv_content)
    #
    # print(f"Filtered waveform data saved at: {fileName}")

    if delete_file:
        write(f'FILESystem:DELEte \"{src_path}\"') # Image data has been transferred to PC and saved. Delete image file from instrument's hard disk.

    print("file transferred successfully\r\n")


def find_matching_files(prefix):
    """Retrieve all filenames from the oscilloscope that start with the given prefix."""
    file_list = query("FILESystem:DIR?")  # Get file list from oscilloscope
    files = file_list.split(",")  # Convert response into a list

    matching_files = []
    # Find files that start with the prefix
    for file in files:
        replaced_file = file.strip().replace('"', '')
        if replaced_file.startswith(prefix):
            matching_files.append(replaced_file)  # Append to the list
            print(replaced_file)

    return matching_files

def get_measurement(num):
    val = query("MEASU:MEAS" + str(num) + ":VAL?")
    # print(str(val) + "\r\n")
    return val

def save_waveforms_on_trigger(format_choice: str = "internal", series_number: int = 1, retry_count: int = 1):
    format_choice = format_choice.strip().lower()

    if format_choice not in ["internal", "spreadsheet"]:
        print(f"Invalid format '{format_choice}'. Defaulting to 'internal'.")
        format_choice = "internal"

    # Set the file format
    write(f"SAVEON:WAVEform:FILEFormat {format_choice}")

    # Set the save location
    write('SAVEON:FILE:DEST "C:/"')

    # Set the filename with series number
    filename = f"TriggerEventWaveform_{format_choice}_{series_number}_{retry_count}"
    write(f'SAVEON:FILE:NAME "{filename}"')

    write("SAVEON:WAVEform:SOURce ALL")

    # Enable saving the waveform when a trigger event occurs
    write("ACTONEVent:TRIGger:ACTION:SAVEWAVEform:STATE ON")

    write("ACTONEVent:ENable 1") # enables act on event

    query("*OPC?")

    print("Done\r\n")


def stop_waveform_saving():
    query("*OPC?")

    write("ACTONEVent:TRIGger:ACTION:SAVEWAVEform:STATE OFF")

    write("ACTONEVent:ENable 0") # enables act on event

    print("waveform saving stopped\r\n")


def retrieve_waveforms(base_filename: str, final_dest_folder: str):
    waveform_files = find_matching_files(base_filename)

    for file in waveform_files:
        source_path = "C:/" + str(file)
        transfer_file(source_path, final_dest_folder)
        time.sleep(1)

    print("Transfer completed.\n")

def end():
    scope.close()
    rm.close()


