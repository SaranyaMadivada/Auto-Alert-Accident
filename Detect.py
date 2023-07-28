import smbus
import serial 
from time import sleep
import sys
from time import sleep
#If gps not working, alternative
"""
import json
from urllib.request import urlopen
"""
from twilio.rest import Client

ser = serial.Serial (“/dev/ttyAMA0”)
gpgga_info = “$GPGGA,”
GPGGA_buffer = 0
NMEA_buff = 0
flag = 0
loc=””
addr = 0x68
maxScale = 24 

PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
INT_ENABLE = 0x38
ACC_XOUT_H = 0x3B
ACC_YOUT_H = 0x3D
ACC_ZOUT_H = 0x3F
bus = smbus.SMBus(1)
def MPU_Init():
bus.write_byte_data(addr,SMPLRT_DIV, 7)
bus.write_byte_data(addr,PWR_MGMT_1, 1)
bus.write_byte_data(addr,CONFIG, 0)
bus.write_byte_data(addr,INT_ENABLE, 1)
def convert_to_degrees(raw_value):
decimal_value = raw_value/100.00
degrees = int(decimal_value)
mm_mmmm = (decimal_value – int(decimal_value))/0.6
position = degrees + mm_mmmm
position = “%.4f” %(position)
return position
def readAxes(addr):
data0 = bus.read_byte_data(addr, ACC_XOUT_H+1)
data1 = bus.read_byte_data(addr, ACC_XOUT_H)
data2 = bus.read_byte_data(addr, ACC_YOUT_H+1)
data3 = bus.read_byte_data(addr, ACC_YOUT_H)
data4 = bus.read_byte_data(addr, ACC_ZOUT_H+1)

data5 = bus.read_byte_data(addr, ACC_ZOUT_H)
 #Combine the two bytes and leftshit by 8
x = data0 | data1 << 8
y = data2 | data3 << 8
z = data4 | data5 << 8
 #in case overflow
if x > 32767 :
x -= 65536
if y > 32767:
y -= 65536
if z > 32767 :
z -= 65536
 #Calculate the two’s complement as indicated in the datasheet
x = ~x
y = ~y
z = ~z
return x, y, z
#Function to calculate g-force from acceleration data
def convertToG(maxScale, xAccl, yAccl, zAccl):
 #Caclulate “g” force based on the scale set by user
 #Eqn: (2*range*reading)/totalBits (e.g. 48*reading/2^16)
X = (2*float(maxScale) * float(xAccl))/(2**16);
Y = (2*float(maxScale) * float(yAccl))/(2**16);
Z = (2*float(maxScale) * float(zAccl))/(2**16);
return X, Y, Z
def isDanger(x, y, z):
if abs(x) > 20 or abs(y) > 20 or abs(z) > 20:
""" If GPS not working use this to get location from the network we have connected.
url = ‘http://ipinfo.io/json’
response = urlopen(url)
data = json.load(response)
"""
try:
while True:
received_data = (str)(ser.readline()) #read NMEA string 
received
GPGGA_data_available = received_data.find(gpgga_info) 
#check for NMEA GPGGA string 
if (GPGGA_data_available>0):
GPGGA_buffer = 
received_data.split(“$GPGGA,”,1)[1] #store data coming after “$GPGGA,” string
NMEA_buff = (GPGGA_buffer.split(‘,’))
#nmea_time = []
nmea_latitude = []
nmea_longitude = []
#nmea_time = NMEA_buff[0] #extract time 
from GPGGA string
nmea_latitude = NMEA_buff[1] #extract 
latitude from GPGGA string
nmea_longitude = NMEA_buff[3] #extract 
longitude from GPGGA string
#print(“NMEA Time: “, nmea_time,’\n’)
lat = (float)(nmea_latitude)
lat = convert_to_degrees(lat)
longi = (float)(nmea_longitude)
longi = convert_to_degrees(longi)
loc = “NMEA Latitude:”+ lat+ “ NMEA Longitude:”+ 
longi
flag=1
if (flag==1):
break

except KeyboardInterrupt:
sys.exit(0)
msg = “Person had met with an Accident at location “+loc
print(msg)
accSID = “AC821bb7e081d4aa86fb95afe79189b26f”
authToken = “3dbe85b32f9cfbd3e57be2e1e6a8fa01”
client = Client(accSID, authToken)
message = 
client.api.account.messages.create(to=”+919949286689”,from_=”+17315357765”,body=msg
)
return True
else:
return False
def main():
 #Run this program unless there is a keyboard interrupt
print (“Starting stream”)
while True:
 #initialize LIS331 accelerometer
 #initialize(addr, 24)
MPU_Init()
 
 #Get acceleration data for x, y, and z axes
xAccl, yAccl, zAccl = readAxes(addr)
 #Calculate G force based on x, y, z acceleration data
x, y, z = convertToG(maxScale, xAccl, yAccl, zAccl)
 #Determine if G force is dangerous to human body & take proper action

if isDanger(x, y, z):
break
 #print G values (don’t need for full installation)
print(“Acceleration in X-Axis : %d” %x)
print(“Acceleration in Y-Axis : %d” %y)
print(“Acceleration in Z-Axis : %d” %z)
print(“\n”)
 #Short delay to prevent overclocking computer
sleep(0.2)
if __name__ ==”__main__”:
main(