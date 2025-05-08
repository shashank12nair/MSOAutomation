from helper_functions import *
from wfrmReader import *

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


#for special purpose. To find optimal voltage for scintillator/pmt modules.
def coincidence_counter(npz_folder: str, channel_number: int, threshold: float = 0.2):
    total_trigger_counter = 0
    pulse_present_counter = 0
    ch_str = f"ch{channel_number}"

    # List all .npz files
    npz_files = [f for f in os.listdir(npz_folder) if f.lower().endswith(".npz")]

    if not npz_files:
        print("No .npz files found in the specified folder.")
        return

    for npz_file in npz_files:
        if ch_str in npz_file.lower():
            total_trigger_counter += 1
            npz_path = os.path.join(npz_folder, npz_file)
            try:
                data = np.load(npz_path)
                voltage = data['voltage']
                voltage_trimmed = voltage[:10000]

                if np.max(voltage_trimmed) > threshold:
                    pulse_present_counter += 1

            except Exception as e:
                print(f"[ERROR] Failed to process {npz_file}: {e}")

    print("\n[RESULT]")
    print(f"Total trigger events: {total_trigger_counter}")
    print(f"Total num. of 3 fold coincidence: {pulse_present_counter}\n")
    return total_trigger_counter, pulse_present_counter


def soft_ltd(npz_folder: str, channel_number: int, threshold: float = 0.2):
    total_trigger_counter = 0
    pulse_present_counter = 0
    ch_str = f"ch{channel_number}"

    # List all .npz files
    npz_files = [f for f in os.listdir(npz_folder) if f.lower().endswith(".npz")]

    if not npz_files:
        print("No .npz files found in the specified folder.")
        return

    for npz_file in npz_files:
        if ch_str in npz_file.lower():
            total_trigger_counter += 1
            npz_path = os.path.join(npz_folder, npz_file)
            try:
                data = np.load(npz_path)
                voltage = data['voltage']
                voltage_trimmed = voltage[:10000]

                if np.max(abs(voltage_trimmed)) > threshold:
                    pulse_present_counter += 1

            except Exception as e:
                print(f"[ERROR] Failed to process {npz_file}: {e}")

    print("\n[RESULT]")
    print(f"Total trigger events: {total_trigger_counter}")
    print(f"Total pulses above threshold: {pulse_present_counter}\n")
    return total_trigger_counter, pulse_present_counter



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

    # Get retry count
    try:
        retry_count = int(input("Enter number of times you want retry: ").strip())
    except ValueError:
        print("Invalid count. Defaulting to 1.")
        retry_count = 1

    # channel number in which 3-fold is connected
    try:
        channel_num = int(input("Enter channel number to analyze (1-4): ").strip())
    except ValueError:
        print("Invalid num. Defaulting to 4.")
        channel_num = 4

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    dest_base_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'))

    # Create the directory if it doesn't exist
    os.makedirs(dest_base_path, exist_ok=True)

    # dest_base_path = "D:/pythonProjects/MSOAutomation/data"  # base data folder
    dest_base_path = os.path.join(dest_base_path, f"wfrm_data_series{series_number}_{timestamp}/")
    for i in range(retry_count):
        # Start waveform saving
        save_waveforms_on_trigger(format_choice, series_number, i+1)

        # Wait for specified duration
        print(f"Waiting for {wait_time} seconds while acquisition runs...")
        time.sleep(wait_time)

        # Stop acquisition
        stop_waveform_saving()

        time.sleep(0.5)

        final_dest_folder = os.path.join(dest_base_path,f"{i + 1}/")
        os.makedirs(final_dest_folder, exist_ok=True)
        print(f"[INFO] Created folder for waveforms: {final_dest_folder}")

        # Retrieve waveform files
        filename_pattern = f"TriggerEventWaveform_{format_choice}_{series_number}_{i + 1}"
        retrieve_waveforms(filename_pattern, final_dest_folder)

        time.sleep(0.5)
        # dest_path = "D:/pythonProjects/MSOAutomation/data/"
        convert_wfm_to_npz(final_dest_folder, show_plot=False)# make this true if you want to see plot of individual files.

        time.sleep(0.5)

        # path to npz file folder
        npz_files_path = os.path.join(final_dest_folder, f"converted_npz/")

        total_trigger_counter, pulse_present_counter = coincidence_counter(npz_files_path, channel_num)

        csv_file = os.path.join(dest_base_path, "coincidence_summary.csv")
        file_exists = os.path.isfile(csv_file)

        with open(csv_file, mode='a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Total trigger(2 fold coincidence)", "Pulse found (3 fold coincidence)", "Timestamp"])
            writer.writerow([total_trigger_counter, pulse_present_counter, timestamp])


if __name__ == "__main__":
    main()
    end()   