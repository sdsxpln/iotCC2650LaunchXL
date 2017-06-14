from bluepy.btle import UUID, Peripheral, DefaultDelegate, AssignedNumbers
import struct
import math
import time
import sys
import argparse
import signal
import sys
from functools import partial 


def _TI_UUID(val):
    return UUID("%08X-0451-4000-b000-000000000000" % (0xF0000000+val))

FIREALARM_MAC = '24:71:89:1B:D0:85'

fireSens = 0


class SensorBase:
    periph = None
    def __init__(self, ):
        Peripheral.__init__(self,addr)
        self.periph = Peripheral
        svcs = self.discoverServices()
        print(svcs)



class AlarmCtrl:
    svcUUID = ("%08X-0451-4000-b000-000000000000" % (0xF0000000+0x1110))
    data0UUID = ("%08X-0451-4000-b000-000000000000" % (0xF0000000+0x1111))
    service = None
    data0 = None

    def __init__(self,Peripheral):
        self.periph = Peripheral

    def enable(self):
        if self.service is None:
            print(self.svcUUID)
            self.service = self.periph.getServiceByUUID(self.svcUUID)
            print("Service find")
            print(self.service)
        if self.data0 is None:
            self.data0 = self.service.getCharacteristics(self.data0UUID)[0]

    def alarmWrite(self,value):
        if (value == 1) :
            self.data0.write(struct.pack("B",0x01))
        else:
            self.data0.write(struct.pack("B",0x00))



class FireRcv:
    
    svcUUID = ("%08X-0451-4000-b000-000000000000" % (0xF0000000+0x1120))
    btn1UUID = ("%08X-0451-4000-b000-000000000000" % (0xF0000000+0x1122))

    service = None
    btn1_data = None
    noti_cntl = None

    def __init__(self,Peripheral):
        self.periph = Peripheral

    def enable(self):
        if self.service is None:
            print(self.svcUUID)
            self.service = self.periph.getServiceByUUID(self.svcUUID)
            print("Service find")
            print(self.service)
        
        if self.btn1_data is None:
            self.btn1_data = self.service.getCharacteristics(self.btn1UUID)[0]
            print("btn1_data find")
            print(self.btn1_data)


    def notienable(self):
        if self.noti_cntl is None:
            self.noti_cntl = self.service.getDescriptors(forUUID=0x2902)[1]
            self.noti_cntl.write(struct.pack('<bb', 0x01, 0x00), True)


class FireDelegate(DefaultDelegate):

    def __init__(self):
        DefaultDelegate.__init__(self)
        self.lastVal = 0
        
    def handleNotification(self, hnd, data):
        global fireSens

        val = struct.unpack("B", data)[0]
        print("noti value = %d" % int(val))
        #input fireSens Status
        fireSens = int(val)



#MAIN Process Class
class FireAlarmBoard(Peripheral):
    
    def __init__(self,addr):
        Peripheral.__init__(self,addr)
        svcs = self.discoverServices()
        print(svcs)
        
        self.AlarmCtrl = AlarmCtrl(self)
        self.FireRcv = FireRcv(self)



def main():

    global fireSens
    prev = 0
    print('Connecting to ' + FIREALARM_MAC)

    bd = FireAlarmBoard(FIREALARM_MAC)
    bd.AlarmCtrl.enable()
    bd.FireRcv.enable()

    bd.setDelegate( FireDelegate() )
    bd.FireRcv.notienable()

    bd.AlarmCtrl.alarmWrite(1)


    try:
        
        while True:
            if bd.waitForNotifications(0.1) :
                print('fireSents = %d' % fireSens)
                if fireSens :
                    print('write 1')
                    bd.AlarmCtrl.alarmWrite(1)
                else:
                    print('write 0')
                    bd.AlarmCtrl.alarmWrite(0)
            
            time.sleep(0.1)


    except KeyboardInterrupt:
        bd.disconnect()
        del bd
        exit()


if __name__ == "__main__":
    main()
