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


from bluepy.btle import Scanner, DefaultDelegate
import time
import struct
import threading
import tkinter
from tkinter import *
from bluepy import btle
import packBTSend as pks


btle_peri = None
t1 = None
devInfoA = []
chHandlerDict = {}

gui = Tk()
gui.title("Gard Charger beta")

pk = pks.packBTSend()

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
			vf = (sbuf[2] + sbuf[3] * 256) /1000.0
			af = (sbuf[4] + sbuf[5] * 256) /1000.0
			cf = (sbuf[6] + sbuf[7] * 256 + sbuf[8] * 65536 + sbuf[9] * 16777216) / 1000.0
			tf = (sbuf[10] + sbuf[11] * 256 + sbuf[12] * 65536 + sbuf[13] * 16777216) /1000.0
			rf = (sbuf[14] + sbuf[15] * 256) / 1000.0
           # print("Voltage = {:.3f}V Current={:.3f}A  R= {:.2f}ohm cap= {:.1f}mAH et= {:.1f}Sec".format(vf, af , rf, cf , tf))
            #(on,vf,af,cf,tf,rf) = struct.unpack('b2H2IH', bytearray(sbuf))
			a.set("{:.3f}".format(af))
			v.set("{:.3f}".format(vf))
			w.set("{:.3f}".format(vf*af))
			c.set("{:.1f}".format(cf))
            
  
def btle_run():
	global btle_peri
	while True:
		try:
			if btle_peri.waitForNotifications(1.0):
			# handleNotification() was called
				continue
		except:
			continue
			
			
def update_gui():
	print("GUI Update")

CHAR_UUID = ["FFE1","FFE2"] #[TX, RX]

def ble_connect():
	global btle_peri
	global t1
	global CHAR_UUID
	
	if not lsb.curselection():
		print("No device selected")
		return
	
	print("Connect...{}".format(lsb.get(lsb.curselection())))
	'''
	if not lsb.get(lsb.curselection()):
		ws = readDeviceInfo()
		macString = ws[0]
		devString = ws[1]
		print("--from---file---")
	else:
		macString = lsb.get(lsb.curselection())[0]
		devDtring = lsb.get(lsb.curselection())[1]
		print("--from---List---")
	'''
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

on = 0
def ble_onOff():
	global btle_peri
	global CHAR_UUID
	global on
	 
	if on == 0:
		on = 1
	else:
		on = 0
	
	if btle_peri:
		try:
			x = pk.packTXdata(1,on) 				 
			chars = btle_peri.getServiceByUUID('FFF0').getCharacteristics(forUUID ='FFF5')
			for ch in chars:
				handle = ch.handle
			if ch.handle:
				print("char:{:}  handle:{:d}".format(ch,ch.handle))
				btle_peri.writeCharacteristic(ch.handle,bytearray(x),withResponse=False)
		except:
			print("Exception----")
			pass

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
	frame_1 = Frame(height = 285, width = 480, bd = 3, relief = 'groove').place(x = 7, y = 5)
	
	text = Text(width = 65, height = 5)
    #Label
	
	#threads
	t2 = threading.Thread(target = update_gui)
	t2.daemon = True
	t2.start()
    
    #Labels
	varDeviceName = StringVar()
	Label(text = "Data1:",textvariable = varDeviceName).place(x = 15, y= 10)
	Label(text = "Current(A)", font=("Arial Bold", 15)).place(x = 15, y= 25)
	Label(text = "Voltage(V)", font=("Arial Bold", 15)).place(x = 240, y= 25)
	Label(text = "Watts(W)", font=("Arial Bold", 15)).place(x = 15, y= 150)
	Label(text = "Capacity(mAH)", font=("Arial Bold", 15)).place(x = 240, y= 150)
	
	v = StringVar()
	v.set("volt")
	a = StringVar()
	a.set("Amp")
	w = StringVar()
	w.set("Watt")
	c = StringVar()
	c.set("mAH")

	vl = Label(textvariable= v , font=("Arial Bold", 50), fg = 'cyan').place(x = 240 , y= 50)
	al = Label(textvariable= a ,font=("Arial Bold", 50), fg = 'orange').place(x = 15 , y = 50)
	wl = Label(textvariable= w ,font=("Arial Bold", 50), fg = 'green').place(x = 15 , y= 180)
	cl = Label(textvariable= c ,font=("Arial Bold", 45), fg = 'green').place(x = 240 , y= 185)
	
	#button
	disconnect = Button(text = "Disconnect", command = ble_disconnect, width = 8).place(x = 240, y = 460)
	connect    = Button(text = "Connect", command = ble_connect, width = 8).place(x = 120, y = 460)
	scan       = Button(text = "BLE Scan", command = ble_scan, width = 8).place(x =15, y = 460)
	
	#onOff = Button(text = "ON/OFF", command = ble_onOff, width = 8).place(x =360, y = 460)
	
	#listBox
	varScan = StringVar()
	lsb = Listbox(listvariable = varScan , width = 59 , height = 9)
	lsb.place(x = 7, y = 300) 

	#mainloop
	gui.geometry("500x500")
	gui.mainloop()
