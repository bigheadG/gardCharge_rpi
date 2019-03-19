'''
This is a Beta Python software for enabling GardCharge GC101 
Smart USB Timer Charger Protector or GardCharge GC101PM Smart
USB Power Meter hardware device to work as Data-Acquisition
Unit (for reading Voltage, Current, and Power info) wirelessly 
connected via Bluetooth Low Energy (BLE) on a Raspberry Pi.  
Note that this Beta software only works as one-direction data 
reading from GardCharge (Tx) to Raspberry Pi (Rx), while not able 
to send control command from Raspberry Pi (Tx) to GardCharge (Rx).
 
It will be great for those who are more knowledgeable on 
Raspberry Pi’s BLE Tx to further support the cause to make GardCharge 
work BOTH as Data Acquisition (Rx) AND as Command Control (Tx) device.
 
Nonetheless, GardCharge as Data-Acquisition Unit 
(for Voltage / Current / Power data sensing) alone for Raspberry Pi 
may perform for various IoT applications.

install bluepy

$sudo install bluepy

Test on: raspberry pi 3 model B
	raspberry pi 3 model A+

BLE Gardcharge BLE Service:

tx_service_UUID			 = "FFF0"
tx_Characteristic_UUID   = "FFF5"

rx_service_UUID          = "FFE0"
rx_Characteristic_UUID   = "FFE2" (notification)
'''
from bluepy import btle
import time


class MyDelegate(btle.DefaultDelegate):
    def __init__(self, params):
        btle.DefaultDelegate.__init__(self)
        # ... initialise here

    def handleNotification(self, cHandle, data):
        # ... perhaps check cHandle
        #print("handler:{:d}  {:d}".format(cHandle,len(data)))
        # ... process 'data'
        if len(data) != 20:
            return
        if not(data[0] == 0x28 and data[19] == 0x29):
            return
            
        sbuf = []
        i = 2
        #data decrypt
        for x in data[2:18]:
            d = x ^ (i ^ data[18]) ^ 0x38 
            sbuf.append(d)
            i += 1
        #print("ch: {:d}".format(sbuf[0]))
        if sbuf[0] == 0x4a: #mode(0x4a)per second response from GardCharge 
            on = sbuf[1]
            vf = (sbuf[2] + sbuf[3] * 256) /1000.0
            af = (sbuf[4] + sbuf[5] * 256) /1000.0
            cf = (sbuf[6] + sbuf[7] * 256 + sbuf[8] * 65536 + sbuf[9] * 16777216) / 1000.0
            tf = (sbuf[10] + sbuf[11] * 256 + sbuf[12] * 65536 + sbuf[13] * 16777216) /1000.0
            rf = (sbuf[14] + sbuf[15] * 256) / 1000.0
            print("Voltage = {:.3f}V Current={:.3f}A  R= {:.2f}ohm cap= {:.1f}mAH et= {:.1f}Sec".format(vf, af , rf, cf , tf))
             

# Initialisation  -------

# Please change Device MAC Address
p = btle.Peripheral("00:1a:c0:00:00:cc")

# Set call back for notifcation
p.setDelegate( MyDelegate("USBC.    0000CCE645") )

# Main loop --------


while True:
    if p.waitForNotifications(1.0):
        # handleNotification() was called
        continue

    print("Waiting...")
    # Perhaps do something else here
    
