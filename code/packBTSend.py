
class Gdefine:
	CMD_DRIVE = 1,
	CMD_CUTOFF_TIME = 2
	CMD_TIMER_EN = 3
	CMD_READ_MEM = 4
	CMD_READ_MEM_A = 4
	CMD_FACT_INIT = 5
	CMD_SAMPLE_TIME = 6
	CMD_READ_CONFIG = 7
	CMD_ERASE_QUE = 8
	CMD_RUN_TEST  = 9
	CMD_SET_TRIP_AMP = 11
	CMD_SET_OFFTIME = 12
	CMD_READ_CONFIG_2 = 14
	CMD_OFFLINE_ENABLE = 17
	
	
	
	
class packBTSend:	
	flow = 0			
	def packTXdata(self,mode,data):
		outBuf = [0xaa for i in range(20)]
		inBuf  = [0xaa for i in range(20)]
		inBuf[2] = mode

		#outBuf no decrypt
		outBuf[0]  = 40
		outBuf[1] = self.flow
		outBuf[19] = 41
		
		if mode == 1 or mode == 3 or mode == 4 or mode == 6 or mode == 11 or mode == 17:
			inBuf[3] =  (data & 0x000000FF)
		elif mode == 2: #CMD_CUTOFF_TIME
			inBuf[4] = data & 0x000000FF
			inBuf[5] = (data & 0x0000FF00) >> 8
			inBuf[6] = (data & 0x00FF0000) >> 16
			inBuf[7] = (data & 0xFF000000) >> 24
		elif mode == 12: #CMD_SETOFF_TIME
			inBuf[3] = data & 0x000000FF
			inBuf[4] = (data & 0x0000FF00) >> 8
			inBuf[5] = (data & 0x00FF0000) >> 16
		
		#print("inBuf:{}".format(inBuf))
		# encrypt
		i = 2
		for x in inBuf[2:17]:
			d = x ^ ((i ^ inBuf[18]) ^ 0x38)
			outBuf[i] = d
			i += 1
            
		self.flow += 1
		self.flow = self.flow % 10 
		#print("flow = {:d}".format(self.flow))
		return outBuf
	
	

	
