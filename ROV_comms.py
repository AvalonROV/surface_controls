import serial
import serial.tools.list_ports
from PyQt5.QtCore import QThread, pyqtSignal

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
    All messages sent from the ROV should be terminated with '\n'
    """
    def __init__(self, baud_rate = 115200):
        self.ser = serial.Serial(timeout=1)
        self.ser.baudrate = baud_rate
    
    def update_port(self, new_port):
        self.ser.port = new_port
        self.ser.open()
        print("Serial port changed to:" + new_port)
    
    def is_open(self):
        return self.seris_open
        
    def end_comms(self):
        self.ser.close()
        print("Serial port closed")
    
    def get_telemetry(self):
        self.ser.write('GT\n'.encode('ascii'))
        data = self.ser.readline().strip().decode('ascii').split(',')
        return {
                "depth" : data[1] + "m",
                "temprature" : data[2] + "C",
                "ph" : data[3],
                "pitch_angle" : data[4] + "deg",
                "roll_angle" : data[5] + "deg"
                }
        '''return {
                "depth" : "1.23m",
                "temprature" : "21.64C",
                "ph" : "7.15",
                "pitch_angle" : "0deg",
                "roll_angle" : "0deg"
                }'''
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
        payload = 'SDC' + str(p) + ',' + str(i) + ',' + str(d) + '\n'
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
    
    def testing_function(self, payload):
        payload += "\n"
        self.ser.write(payload.encode('ascii'))
        data = self.ser.readline().strip().decode('ascii')
        print(data)
        
if __name__ == "__main__":
    comms = Serial()
    comms.update_port('COM7')
    while(1):
        comms.testing_function("Hello World!")