import serial
import serial.tools.list_ports as ls_port
from PyQt5.QtCore import QThread, pyqtSignal
import sys 

class ls_COM_ports(QThread):
    signal = pyqtSignal(list)
    
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.old_list = []
        
    def run(self):
        self.running = True
        while self.running:
            new_list = [comport.device for comport in serial.tools.list_ports.comports()]
            if self.old_list != new_list:
                self.signal.emit(new_list)
                self.old_list = new_list
                print(self.old_list)
            
        print("Port listing thread terminating")

class Serial:
    """
    port  --> COM(X) for windows systems, dev/tty/USB(X) for linux based system
    baud_rate ---> {9600, 152000.. etc}
    """
    def __init__(self, baud_rate = 115200):
        self.ser = serial.Serial()
        self.ser.baudrate = baud_rate
    
    def update_port(self, new_port):
        self.ser.port = new_port
        print("Serial port changed to:" + new_port)
    
    def is_open(self):
        if self.ser.port == None:
            return False
        else:
            return True
        
    def end_comms(self):
        self.ser.close()
        print("Serial port closed")
    
    def get_telemetry(self):
        self.ser.write('GT\n'.encode('ascii'))
        data = self.ser.readline().strip().decode('ascii')
        return data
    
    def set_thrsuters(self, power):
        payload = 'ST\n'
        for value in power:
            payload += str(value)
        self.ser.write(payload.encode('ascii'))
    
    def set_camera(self, channel, ID):
        payload = 'SC' + channel + ID + '\n'
        self.ser.write(payload.encode('ascii'))
    
    def set_gripper(self):
        payload = 'SG\n'
        self.ser.write(payload.encode('ascii'))
    
    def open_trap_door(self):
        payload = 'OTD\n'
        self.ser.write(payload.encode('ascii'))
    
    def set_depth_pid_state(self, state):
        payload = 'SDCS\n' + str(state) + '\n'
        self.ser.write(payload.encode('ascii'))
    
    def set_depth_pid(self, p, i, d):
        payload = 'SDC\n' + str(p) + ',' + str(i) + ',' + str(d) + '\n'
        self.ser.write(payload.encode('ascii'))
    
    def set_pitch_pid_state(self, state):
        payload = 'SPCS\n' + str(state) + '\n'
        self.ser.write(payload.encode('ascii'))
    
    def set_pitch_pid(self, p, i, d):
        payload = 'SPC' + str(p) + ',' + str(i) + ',' + str(d) + '\n'
        self.ser.write(payload.encode('ascii'))
    
    def set_depth_calibration(self, p, i, d):
        payload = 'SD_trim\n'
        self.ser.write(payload.encode('ascii'))
        
if __name__ == "__main__":
    comms = SerialComms('COM6')
    while(1):
        try:
            print(comms.getPotentiometerValues())
        except:
            comms.end_comms()
            print("Port cLosed!")
            sys.exit()