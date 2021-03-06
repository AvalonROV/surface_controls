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

class Serial(QThread): 
    """
    port  --> COM(X) for windows systems, dev/tty/USB(X) for linux based system
    baud_rate ---> {9600, 152000.. etc}
    All messages sent from the ROV should be terminated with '\n'
    """
    signal = pyqtSignal(str)
    
    telemetry = {
            "temp" : "N/A",
            "pH" : "N/A",
            "humidity" : "N/A",
            "depth" : "N/A",
            "roll" : "N/A",
            "pitch" : "N/A"
            }
    
    def __init__(self, baud_rate = 115200, parent=None):
        QThread.__init__(self, parent)
        self.ser = serial.Serial(timeout=0.01)
        self.ser.baudrate = baud_rate
        
        self.running = True
        self.Tx_payload_queue = []
        
    def update_port(self, new_port):
        self.ser.port = new_port
        self.ser.open()
        print("Serial port changed to:" + new_port)
    
    def is_open(self):
        return self.seris_open
    
    def run(self):
        
        while self.running:
            #--Rx-------------------------------------------------------------#
            
#            print(data)
            try:
                data = self.ser.readline().strip().decode('ascii')
#                print(data)
                if data[0] == "R":
                    if data[1] == "A": # Temprature
                        self.telemetry["temp"] = str(data[2:])
                    
                    elif data[1] == "B": # humidity:
                        self.telemetry["pH"] = str(data[2:])
                    
                    elif data[1] == "C": # roll angle
                        self.telemetry["depth"] = str(data[2:])
                    
                    elif data[1] == "D": # pitch angle
                        self.telemetry["roll"] = str(data[2:])
                        
                    elif data[1] == "E": # pitch angle
                        self.telemetry["pitch"] = str(data[2:])
                    
                    elif data[1] == "F": # pitch angle
                        self.telemetry["humidity"] = str(data[2:])
                    
                    else:
                         self.signal.emit(">> Error: undefined message received.")
                         
                else:
                    self.signal.emit(">> Error: missing \"R\" at the start of the message.")
                self.signal.emit(">> " + data)
                
            except Exception as e:
                print(e)
#                self.signal.emit("ERROR: Issue with data received:")
#                self.signal.emit(str(e))
            
            time.sleep(0.01)
        
    def end_comms(self):
        self.running = False
        self.ser.close()
        print("Serial port closed")
        
    def set_thrsuters(self, power):
        payload = 'SA' + power + '!'
        self.ser.write(payload.encode('ascii'))
        return "<< " + payload
    
    def set_pid_controller_gains(self, controller, p, i, d):
        if controller == "depth":
            payload = 'SB'
        elif controller == "pitch":
            payload = 'SC'
        
        payload += str(p) + ',' + str(i) + ',' + str(d) + '!'
        self.ser.write(payload.encode('ascii'))
        return "<< " + payload
    
    def set_pid_controller_state(self, controller, state):
        if controller == "depth":
            payload = 'SD' + str(state) + '!'
        elif controller == "pitch":
            payload = 'SE' + str(state) + '!'
        
        self.ser.write(payload.encode('ascii'))
        return "<< " + payload
    
    def set_manipulator(self, manipulator, state):
        
        if manipulator == "dispenser": 
            payload = 'SF'
        elif manipulator == "cannon_gripper": 
            payload = 'SG'
        elif manipulator == "gripper": 
            payload = 'SH'
        elif manipulator == "lift_bag": 
            payload = 'SI'
        elif manipulator == "micro_rov": 
            payload = 'SJ'
        
        payload += str(state) + '!'
        print(payload)
        self.ser.write(payload.encode('ascii'))
        return "<< " + payload
    
    def set_camera(self, channel, camera):
        if channel == 1:
            payload = 'SK'+ str(camera) + '!'
        elif channel == 2:
            payload = 'SL' + str(camera) + '!'
        
        print(payload)
        self.ser.write(payload.encode('ascii'))
        return "<< " + payload
    
    def pid_init(self, t1, t2, f1, f2):
        payload = 'SO' + str(t1) + str(t2) + str(f1) + str(f2) +  '!'
        self.ser.write(payload.encode('ascii'))
        return "<< " + payload
    
    def trim_depth_sensor(self):
        payload = 'SM!'
        self.ser.write(payload.encode('ascii'))
        return "<< " + payload
    
    def trim_imu(self):
        payload = 'SN!'
        self.ser.write(payload.encode('ascii'))
        return "<< " + payload
    
    
    def testing_function(self, payload):
        payload += "!"
#        self.ser.write(payload.encode('ascii'))
        data = self.ser.readline().strip().decode('ascii')
#        print(data)
        
if __name__ == "__main__":
    comms = Serial()
    comms.update_port('COM11')
    while(1):
        comms.testing_function("SA500500500500500600!")
        time.sleep(0.1)