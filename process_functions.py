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
