# gardCharge for rpi

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

# Measure data:
    Voltage , Current , Watt , mAH

# Install bluepy
    $sudo pip3 install bluepy
    
# Hardware:

    raspberry pi 3 model B
    raspberry pi 3 model A+
    GC101 - USB Power Meter hardware device

# Communication Protocol:
Detailed information please reference:
    
    /Doc/USBCurrentProjectDocE619.pdf
  
# Gardcharge BLE Service & Characteristic:
    tx_service_UUID          = "FFF0"
    tx_Characteristic_UUID   = "FFF5"
    rx_service_UUID          = "FFE0"
    rx_Characteristic_UUID   = "FFE2" (notification)

# python package:
    TKinter
    bluepy

# Example program:
    gardcharge.py :Show voltage,current,watt & charge capacity in terminal
    GardCharge_GUI.py :Show voltage,current,watt & charge capacity in GUI
    GardCharge_GUI_plot.py :Updating power consumption real time wavefrom

# gardcharge.py screen shot:

![alt text](https://github.com/bigheadG/gardCharge_rpi/blob/master/gardcharge.png)

# GardCharge_GUI.py screen shot:

![alt text](https://github.com/bigheadG/gardCharge_rpi/blob/master/gui.png)

# GardCharge_GUI_plot.py screen shot(waveform animation):

![alt text](https://github.com/bigheadG/gardCharge_rpi/blob/master/2019-03-29-042316_640x514_scrot.png)

