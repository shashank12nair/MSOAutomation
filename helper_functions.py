from mso_comm import *

from datetime import datetime  # std library

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

# For socket comm
def write_socket(command):
    try:
        sock.sendall((command + "\n").encode()) #send command
        response = sock.recv(4096).decode().strip()
        return response
    except:
        print("socket write operation failed.Try again.\r\n")
        return


def capture_image():
    write('SAVE:IMAGe \"C:/Temp.png\"')    # Save image to instrument's local disk

    dt = datetime.now()    # Generate a filename based on the current Date & Time
    fileName = dt.strftime("C:/Users/seema/PycharmProjects/MSOAutomation/Images/IMG_%Y%m%d_%H%M%S.png")

    query('*OPC?')# Wait for instrument to finish writing image to disk

    write('FILESystem:READFile \"C:/Temp.png\"') # Read image file from instrument
    imgData = read_raw(1024 * 1024)

    file = open(fileName, "wb")  # Save image data to local disk
    file.write(imgData)
    file.close()

    write('FILESystem:DELEte \"C:/Temp.png\"') # Image data has been transferred to PC and saved. Delete image file from instrument's hard disk.
    print("Image captured successfully\r\n")


def get_measurement(num):
    val = query("MEASU:MEAS" + str(num) + ":VAL?")
    # print(str(val) + "\r\n")
    return val
