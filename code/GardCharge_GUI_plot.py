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

install matplotlib

$sudo pip3 install matplotlib

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


from bluepy.btle import Scanner, DefaultDelegate
import time
import struct
import threading

from tkinter import *
import tkinter as tk
from bluepy import btle
import packBTSend as pks

# for plot v/i waveform
import numpy as np
from collections import deque
from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib.figure import Figure

class gcPara:
	def __init__(self, vf,af,cf,wf,rf,tf):
		self.vf = vf
		self.af = af
		self.cf = cf
		self.wf = wf
		self.rf = rf
		self.tf = tf
	
gc = gcPara(0.0,0.0,0.0,0.0,0.0,0)	 	

maxlen = 101
tr0 = deque([0.0] * maxlen, maxlen=maxlen)
tr1 = deque([0.0] * maxlen, maxlen=maxlen)
tr2 = deque([0.0] * maxlen, maxlen=maxlen)
tr3 = deque([0.0] * maxlen, maxlen=maxlen)
tr4 = deque([0.0] * maxlen, maxlen=maxlen)

 

btle_peri = None
t1 = None
devInfoA = []
chHandlerDict = {}

gui = tk.Tk()
back = tk.Frame(master=gui, width=500, height=265, bg='gray')
back.pack()


gui.title("GardCharge GC-101")
pk = pks.packBTSend()

fig = plt.figure()
fig.suptitle("GardCharge")
ax = plt.axes(xlim=(0,maxlen), ylim=(0.0, 18.0))
ax.set(title="Power Consumption Waveform", ylabel ="Volt/Amp/Watt")
ax1 = ax.twinx()
ax1.set(title="",ylabel= "mAH", xlim =(0,100),ylim = (0,1500))
color = 'green'
ax1.set_ylabel('mAH', color=color) 


a0, = ax.plot([], [], c = "cyan")   #v
a1, = ax.plot([], [], c = "orange") #a
a2, = ax.plot([], [], c = "red")    #w
a3, = ax1.plot([], [], c = "green")  #c
 
tr0Text = ax.text(1,17,"volt",fontsize = 14,bbox=dict(facecolor='cyan', alpha=0.25))
tr1Text = ax.text(35,17,"Amp",fontsize = 14,bbox=dict(facecolor='orange', alpha=0.25))
tr2Text = ax.text(70,17,"Watt",fontsize = 14,bbox=dict(facecolor='red', alpha=0.25))
tr3Text = ax.text(1,15.5,"mAH",fontsize = 14,bbox=dict(facecolor='green', alpha=0.25))
tr4Text = ax.text(70,15.5,"Ω",fontsize = 14,bbox=dict(facecolor='yellow', alpha=0.25))

yLimit = 100
aylim  = 10

def update(i,a0,a1,a2,a3):
	global yLimit
	global aylim
	 
	yLimit = yLimit if yLimit >= max(tr3) else yLimit + 100
	yLimit = 100 if max(tr3) < 100 else yLimit 
			
	ay = max(max(tr0),max(tr2)) 
	aylim = aylim if aylim >= ay else aylim + 2
	aylim = 10 if ay < 10 else aylim
	
	ax1.set(title="",ylabel= "mAH", xlim =(0,100),ylim = (0,yLimit))
	ax.set(xlim =(0,100),ylim = (0,aylim))
	 
	tr0Text.set_position((1,aylim *0.94))
	tr1Text.set_position((35,aylim *0.94))  
	tr2Text.set_position((70,aylim *0.94)) 
	tr3Text.set_position((1,aylim *0.84)) 
	tr4Text.set_position((70,aylim *0.84)) 
	
	a0.set_data(np.arange(len(tr0)), tr0)
	a1.set_data(np.arange(len(tr1)), tr1)
	a2.set_data(np.arange(len(tr2)), tr2)
	a3.set_data(np.arange(len(tr3)), tr3)
	 
	return a0,a1,a2,a3 


class ScanDelegate(btle.DefaultDelegate):
	def __init__(self):
		btle.DefaultDelegate.__init__(self)

	def handleDiscovery(self, dev, isNewDev, isNewData):
		if isNewDev:
			print("Discovered device", dev.addr)
		elif isNewData:
			print("Received new data from", dev.addr)

class cmdDelegate(btle.DefaultDelegate):
	def __init__(self):
		btle.DefaultDelegate.__init__(self)
	def handleCmd(self):
		print("----------cmdDelegate-------------")
	

class MyDelegate(btle.DefaultDelegate):
	
	def __init__(self, params):
		btle.DefaultDelegate.__init__(self)
		# ... initialise here
		
	def handleNotification(self, cHandle, data):
		global a
		global v
		global w
		global c
		
		#print("----notification-----")
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
                 
		if sbuf[0] == 0x41:
			print("----power on/off---------")
          
        #print("ch: {:d}".format(sbuf[0]))
		if sbuf[0] == 0x4a: #mode(0x4a)per second response from GardCharge 
			on = sbuf[1]
			gc.vf = (sbuf[2] + sbuf[3] * 256) /1000.0
			gc.af = (sbuf[4] + sbuf[5] * 256) /1000.0
			gc.cf = (sbuf[6] + sbuf[7] * 256 + sbuf[8] * 65536 + sbuf[9] * 16777216) / 1000.0
			gc.tf = (sbuf[10] + sbuf[11] * 256 + sbuf[12] * 65536 + sbuf[13] * 16777216) /1000.0
			gc.rf = (sbuf[14] + sbuf[15] * 256) / 1000.0
			gc.wf = gc.af * gc.vf
			 
			tr0.append(gc.vf)
			tr1.append(gc.af)
			tr2.append(gc.wf)
			tr3.append(gc.cf)
			 
			
			tr0Text.set_text("volt={:.2f}V".format(gc.vf))
			tr1Text.set_text("Amp ={:.2f}A".format(gc.af))
			tr2Text.set_text("Watt={:.2f}W".format(gc.wf))
			tr3Text.set_text("Cap.={:.2f}mAH".format(gc.cf))
			tr4Text.set_text("ohm ={:.2f}Ω".format(gc.rf))
			#print("Voltage = {:.3f}V Current={:.3f}A  R= {:.2f}ohm cap= {:.1f}mAH et= {:.1f}Sec".format(gc.vf,gc.af ,gc.rf,gc.cf,gc.tf))
			
			        
    
def btle_run():
	global btle_peri
	global gc
	while True:
		try:
			if btle_peri.waitForNotifications(1.0):
			# handleNotification() was called
				#print("===============add===========")
				continue
		except:
			continue
			
CHAR_UUID = ["FFE1","FFE2"] #[TX, RX]

def ble_connect():
	global btle_peri
	global t1
	global CHAR_UUID
	
	if not lsb.curselection():
		print("No device selected")
		return
	
	print("Connect...{}".format(lsb.get(lsb.curselection())))
	
	try:
		btle_peri = btle.Peripheral(lsb.get(lsb.curselection())[1],"public")
		varDeviceName.set(lsb.get(lsb.curselection())[0])
		btle_peri.setDelegate( MyDelegate("USBC.") )
	except:
		print("Connect Error Exception")
		return
	
	save2file(lsb.get(lsb.curselection())[1] +";" + lsb.get(lsb.curselection())[0])
	t1 = threading.Thread(target = btle_run)
	t1.daemon = True
	t1.start()
	
	
def ble_disconnect():
	print("disconnect...")
	global btle_peri
	if btle_peri:
		btle_peri.disconnect()
		varDeviceName.set("Disconnect")
		t1.signal = False # kill the thread
		
def ble_scan():
	try:
		scanner = Scanner().withDelegate(ScanDelegate())
		devices = scanner.scan(5.0)
		print("-----show devices data: {:d}:".format(len(devices)))
		if devices:   
			devInfoA = [] 
			for dev in devices:
				print("----device:{}".format(dev))
                #print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
                #devInfoA.append((dev.addr, dev.rssi))
				for (adtype, desc, value) in dev.getScanData():
					if desc == "Complete Local Name":
						devInfoA.append((value,dev.addr ,dev.rssi))
						print("%s = %s" % (desc, value))
			print(devInfoA)
		insertScanList(devInfoA)
	except:
		print("Scanner Scan exception")


def ble_pairing():
	x = readDeviceInfo()
	words = x.split(";")   
	print(words)

def save2file(macString):
	file2write=open("device.txt",'w')
	file2write.write( macString)
	file2write.close()

def readDeviceInfo():
	fh = open("device.txt",'r')
	return fh.readline()

def insertScanList(ls):
	lsb.delete('0','end')
	for item in ls:
		lsb.insert('end',item)
	
if __name__ == '__main__':
	'''
	The mainloop contains of all the GUI objects
	'''
	#Frame
	frame_1 = Frame(height = 250, width = 480, bd = 3, relief = 'groove').place(x = 7, y = 5)
	
    #Labels
	varDeviceName = StringVar()
	Label(text = "Data1:",textvariable = varDeviceName).place(x = 15, y= 10)
	
	#listBox
	varScan = StringVar()
	lsb = Listbox(listvariable = varScan , width = 59 , height = 9)
	lsb.place(x = 9, y = 30) 
	
	#button
	disconnect = Button(text = "Disconnect", command = ble_disconnect, width = 8).place(x = 240, y = 190)
	connect    = Button(text = "Connect", command = ble_connect, width = 8).place(x = 120, y = 190)
	scan       = Button(text = "BLE Scan", command = ble_scan, width = 8).place(x =15, y = 190)
	
	#onOff = Button(text = "ON/OFF", command = ble_onOff, width = 8).place(x =360, y = 460)
	
	plt.title("Power Consumption Waveform")
		
	plt.legend()
	plt.grid(linestyle='--', linewidth=0.5, alpha=0.5)
	
	ani = animation.FuncAnimation(fig, update, fargs=(a0,a1,a2,a3), interval=750)
	plt.show()

	#mainloop
	gui.geometry("500x500")
	gui.mainloop()
