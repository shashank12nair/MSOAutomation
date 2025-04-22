# tests the if the communication is okay between pc and MSO
from operator import truediv

import pyvisa
# import socket

visaRsrcAddrTcpIP = "TCPIP0::192.168.0.2::inst0::INSTR" # Visa resource address for TCP/IP interface
visaRsrcAddrUsb = "USB::0x0699::0x0528::C015032::INSTR" # Visa resource address for USB interface
msoIpAddr = "192.168.0.2"
msoSocketPort = 4000



TcpInterfaceFailed = False
UsbInterfaceFailed = False
SocketInterfaceFailed = False

rm = pyvisa.ResourceManager()
print(rm.list_resources())

# scope = rm.open_resource(visaRsrcAddrTcpIP)
# global scope
#
print("Interfacing with TCP/IP\n")

try:
    scope = rm.open_resource(visaRsrcAddrTcpIP)

except:
    TcpInterfaceFailed = True
    print("TCP/IP interfacing failed. Trying with usb interfacing next.\r\n")

if TcpInterfaceFailed:
    try:
        scope = rm.open_resource(visaRsrcAddrUsb)
    except:
        UsbInterfaceFailed = True

if not TcpInterfaceFailed or not UsbInterfaceFailed:
    try:
        instrId = scope.query('*IDN?')
        print("User instrument id is: " + instrId + "\r\n")
        if not TcpInterfaceFailed:
            print("Interfacing with the device completed successfully using TCP/IP\r\n")
        else:
            print("Interfacing with the device completed successfully using USB\r\n")
    except:
        print("Get instrument info command did not work. Communication failed. Try again")
        scope.close()
        rm.close()
else:
    print("Both interfacing options failed.\r\nCheck if the resource addresses is correct.\r\nCheck if the instrument is connected to pc using either ethernet cable or USB 3.0 cable\r\n")

    # print("Trying with socket communication\n")a
    #
    # try:
    #     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create a socket and connect to the mso
    #     sock.connect((msoIpAddr, msoSocketPort))
    #     sock.sendall(("*IDN?" + "\n").encode()) #sending a command to get mso info to test comm.
    #     response = sock.recv(4096).decode().strip()
    #     print(response + "\n")
    #     print("Socket communication successfull.\n")
    #     sock.close()
    #
    # except:
    #     print("Socket communication Failed. Check all connections \r\n. Check if the given IP address and the socket number is correct for socket comm.\r\n")

