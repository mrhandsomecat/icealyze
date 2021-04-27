import Adafruit_DHT
import time
import os
import glob
import serial
from csv import writer
from datetime import datetime
"""
Bluetooth-client
"""
addr = "B8:27:EB:F7:A9:05"  #Adress of server pi

if len(sys.argv) < 2:
    print("No device specified. Searching all nearby bluetooth devices for "
          "the SampleServer service...")
else:
    addr = sys.argv[1]
    print("Searching for SampleServer on {}...".format(addr))

# search for the SampleServer service
uuid = "3092be56-7362-4b7b-b528-b78593ac3d0d"
service_matches = bluetooth.find_service(uuid=uuid, address=addr)

if len(service_matches) == 0:
    print("Couldn't find the SampleServer service.")
    sys.exit(0)

first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

print("Connecting to \"{}\" on {}".format(name, host))

# Create the client socket
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((host, port))

print("Connected. ")

"""
Utilities--------------------------------------------------------------------
"""
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PINS = [2, 3, 27, 22]
now = datetime.now()
t = now.strftime("%H:%M:%S")
(h, m, s) = t.split(':')
ref = int(h) * 3600 + int(m) * 60 + int(s)
def read_temp_raw(n):
    device_folder = glob.glob(base_dir + '28*')[n]
    device_file = device_folder + '/w1_slave'
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
def convert_temp(n):
    lines = read_temp_raw(n)
    while lines[0].strip()[-3:] != 'YES':
        lines = read_temp_raw(n)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        if temp_c > 2048:
            temp_c = temp_c - 4096
        return temp_c
def read_temp():
    temps = []
    for i in range (0, 4):
        temp = convert_temp(i)
        temps.append(temp)
        print("Temp_sensor{} = {}*C.".format(i, temp))
    return temps
def read_humidity():
    h_list = []
    t_list = []
    for i in range(0, 4):
        h, t = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PINS[i])
        if h is not None and t is not None:
            h_list.append(h)
            t_list.append(t)
            print("h{} = {}, t{} = {}.".format(i, h, i, t))
        else:
            print("Failed to read sensor.\n")
    return h_list, t_list
def time_convert(t, ref):
    (h, m, s) = t.split(':')
    time = int(h) * 3600 + int(m) * 60 + int(s) - ref
    return time
"""
Main--------------------------------------------------------------------------
"""
while True:
    print("Initializing...")
    h, h_temps = read_humidity()
    temps = read_temp()
    now = datetime.now()
    time_now = now.strftime("%H:%M:%S")
    data = [time_convert(time_now, ref)]
    for x in h:
        data.append(x)
    for x in temps:
        data.append(x)
    with open('data_lab.csv', 'a') as data_csv:
        writer_obj = writer(data_csv)
        writer_obj.writerow(data)
        data_csv.close()
        #sock.send(data) here you send data over bluetooth 
    time.sleep(2)
sock.close()
