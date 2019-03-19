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
In the demo example we will get the data from GC101 via BLE. For example: In mode 0x4a,periodic echo(page 5 of 12),
can get all of parameters such as voltage, current, charge capacitance, resistance and timer cut-off time for use 
depends your application. The 20 bytes data structure description as following:

        //*************************************************************************************
        //* MODE 0x4A := echo device status per 1 sec periodically
        byteIndex:     0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19
        byteName:      h  f  m  s  v  v in in  c  c  c  c tc tc tc tc  r  r cs  T
        byteName:      (  f 4A  s v1 v0 i1 i0 c3 c2 c1 c0 t3 t2 t1 t0 r1 r0 cs  )
        Notes:
        buf[3] := s := status (0: OFF, 1: ON)
        buf[4..5] := v := voltage (unit: mV)
        buf[6..7] := in := current (unit: mA)
        buf[8..11] := c := capacity (unit: uAH) 
        buf[12..15] := tc := cutOffTime (unit: ms) 
        buf[16..17] := r := resistance (unit: Ohm)
        
        buf[0] := h : Header
        buf[1] := f : flow number
        buf[2] := m : mode
        buf[19]:= T : Tail
        //*************************************************************************************
    
    
    
