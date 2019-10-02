from network import LoRa
from machine import I2C
import sys,  machine
import pycom
import appkeys
import ssd1306
import socket
import time
import binascii
from machine import Pin
from dth import DTH
import ustruct
import utime

# Colors
off = 0x000000
red = 0xff0000
green = 0x00ff00
blue = 0x0000ff
FIVE_MINUTES = 5 * 60

# Turn off hearbeat LED
pycom.heartbeat(False)
th = DTH(Pin('P3', mode=Pin.OPEN_DRAIN),1)
# Initialize LoRaWAN radio
# lora = LoRa(mode=LoRa.LORAWAN)
lora = LoRa(mode=LoRa.LORAWAN)

# Set network keys
app_eui = binascii.unhexlify(appkeys.APP_EUI)
app_key = binascii.unhexlify(appkeys.APP_KEY)

# Switch OFF WLAN
#print("Disable WLAN");
#wlan = WLAN()
#wlan.deinit()
counter = 0

def send_data(result):
    print(counter)
    counter = counter + 1
    print("Temperature: %.1f C" % result.temperature)
    print("Humidity: %.1f %%" % result.humidity)
    
    tempbytes = ustruct.pack('f', result.temperature)
    humiditybytes = ustruct.pack('f', result.humidity)
    databytes = tempbytes + humiditybytes
    s.send(databytes)

def read_sensor():
    result = th.read()
    if result.is_valid():
        # pycom.rgbled(0x001000) # green
        send_data(result) 
    else:
        # pycom.rgbled(0xFF0000) # red
        print("No valid data")

    time.sleep(2.0)


def pin_handler(arg):
    print("got an interrupt in pin %s" % (arg.id()))
    print("----------------------------------------")
    #display("Sending data..",0,40,False)
    read_sensor()



# Join the network
print("Try to Join Network ....")
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0, dr=0)
pycom.rgbled(red)
print("Joining LoRa ...")

# Loop until joined
while not lora.has_joined():
    print('Not joined yet...')    
    pycom.rgbled(blue)
    time.sleep(1.0)
    pycom.rgbled(red)
    time.sleep(2.5)
    

print('Joined')


pycom.rgbled(off)

s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
s.setblocking(True)


# send some data
# s.send(str.encode("connected"))

# make the socket non-blocking
# (because if there's no data received it will block forever...)
s.setblocking(False)

# get any data received (if any...)
data = s.recv(64)
print(data)

# make `P10` an input with the pull-up enabled
p_in = Pin('P10', mode=Pin.IN, pull=Pin.PULL_UP)
p_in.callback(Pin.IRQ_FALLING, pin_handler)
print("waiting for button press")
# display("Waiting for button",0,30,True)
while True:
    time.sleep(2.0)
    read_sensor()
    time.sleep(FIVE_MINUTES)