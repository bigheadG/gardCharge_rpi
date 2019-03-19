# Gardcharge BLE Service:

    tx_service_UUID          = "FFF0"
    tx_Characteristic_UUID   = "FFF5"

    rx_service_UUID          = "FFE0"
    rx_Characteristic_UUID   = "FFE2" (notification)
    
# data Encrypt:
    data length is 20 bytes
    
    def encrypt(data)
        sbuf = []
        i = 2
        for x in data[2:18]:
            d = x ^ (i ^ data[18]) ^ 0x38 
            sbuf.append(d)
            i += 1
        return sbuf
        
    
  
# USB GardCharge Protocol:

    GardCharge GC101 will send out 20 bytes per second after BLE pairing. the 20 bytes data includes command and data.
    In the demo example we get the data from GC101 via BLE. In mode 0x4a,periodic echo(page 5 of 12), can get all of            parameters such as voltage, current, charge capacitance, resistance and timer cut-off time for use depends your application.
    
    
    
