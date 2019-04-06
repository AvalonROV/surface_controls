import serial
import serial.tools.list_ports
import time
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
        self.ser = serial.Serial(timeout=0.1)
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
    
    def get_telemetry(self): # Needs finishing
        self.ser.write('SK\n'.encode('ascii'))
        data = self.ser.readline().strip().decode('ascii').split(',')
        if data[0] == "":
            return{
                "depth" : "N/A",
                "temprature" : "N/A",
                "ph" : "N/A",
                "pitch_angle" : "N/A",
                "roll_angle" : "N/A"
                }
        else:
            return {
                    "depth" : data[1] + "m",
                    "temprature" : data[2] + "C",
                    "ph" : data[3],
                    "pitch_angle" : data[4] + "deg",
                    "roll_angle" : data[5] + "deg"
                    }
        
    def set_thrsuters(self, power):
        payload = 'SA' + power + '!'
        self.ser.write(payload.encode('ascii'))
        return payload
    
    def set_camera(self, channel_1, channel_2):
        payload = 'SH' + channel_1 + channel_2 + '\n'
        self.ser.write(payload.encode('ascii'))
    
    def set_gripper(self):
        payload = 'SF\n'
        self.ser.write(payload.encode('ascii'))
    
    def set_trap_door(self):
        payload = 'SG\n'
        self.ser.write(payload.encode('ascii'))
    
    def set_depth_pid_state(self, state):
        payload = 'SD' + str(state) + '\n'
        self.ser.write(payload.encode('ascii'))
    
    def set_depth_pid(self, p, i, d):
        payload = 'SB' + str(p) + ',' + str(i) + ',' + str(d) + '\n'
        self.ser.write(payload.encode('ascii'))
    
    def set_pitch_pid_state(self, state):
        payload = 'SE' + str(state) + '\n'
        self.ser.write(payload.encode('ascii'))
    
    def set_pitch_pid(self, p, i, d):
        payload = 'SC' + str(p) + ',' + str(i) + ',' + str(d) + '\n'
        self.ser.write(payload.encode('ascii'))
    
    def trim_depth_sensor(self):
        payload = 'SI\n'
        self.ser.write(payload.encode('ascii'))
    
    def trim_imu(self):
        payload = 'SJ\n'
        self.ser.write(payload.encode('ascii'))
    
    def testing_function(self, payload):
        payload += "\n"
        self.ser.write(payload.encode('ascii'))
        data = self.ser.readline().strip().decode('ascii')
        print(data)
        
if __name__ == "__main__":
    comms = Serial()
    comms.update_port('COM11')
    while(1):
        comms.testing_function("SA500500500500500600!")
        time.sleep(0.1)