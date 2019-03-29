This is a Python example program for Raspberry Pi reading GardCharge Power Parameter values (voltage, current, power, etc.)
 via Bluetooth.
 
(1)gardcharge.py: show volt/amp/watt/capacity/ohm in terminal

(2)GardCharge_GUI.py: show volt/amp/watt/capacity/ohm use tkinter GUI package
  use packages: bluepy, tkinter
  
(3)GardCharge_GUI_plot.py: show volt/amp/watt/capacity live update chart use matplotlib.animation package
  use packages: bluepy, tkinter, matplotlib 
  
## (1)gardcharge.py

# import bluepy
    from bluepy import btle
# Connect to GC101
Please find your Device MAC Address: "xx:xx:xx:xx:xx:xx"

    p = btle.Peripheral("00:1a:c0:00:00:cc")

# Set call back for notifcation
    p.setDelegate( MyDelegate("USBC.    0000CCE645") )

# Main loop 
    while True:
      if p.waitForNotifications(1.0):
          # handleNotification() was called
          continue

      print("Waiting...")
    
# Add Delegate
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
