import serial
import serial.tools.list_ports as ls_port
import sys 

def ls_COMports():
    return [comport.device for comport in serial.tools.list_ports.comports()]

class SerialComms:
    """
    port  --> COM(X) for windows systems, dev/tty/USB(X) for linux based system
    baud_rate ---> {9600, 152000.. etc}
    """
    def __init__(self, port, baud_rate = 115200):
        self.ser = serial.Serial(port, baudrate = baud_rate, timeout = 1)
    
    def update_port(self, new_port):
        self.ser.port = new_port
        print("Serial port changed to:" + new_port)
    
    def is_open(self):
        return self.ser.is_open()
    
    def end_comms(self):
        self.ser.close()
        print("Serial port closed")
    
    def get_telemetry(self):
        self.ser.write('GT'.encode('ascii'))
        data = self.ser.readline().strip().decode('ascii')
        return data
    
    def set_thrsuters(self, power):
        payload = 'ST'
        for value in power:
            payload += str(value)
        self.ser.write(payload.encode('ascii'))
    
    def set_camera(self, channel, ID):
        payload = 'SC' + channel + ID
        self.ser.write(payload.encode('ascii'))
    
    def set_gripper(self):
        payload = 'SG'
        self.ser.write(payload.encode('ascii'))
    
    def open_trap_door(self):
        payload = 'OTD'
        self.ser.write(payload.encode('ascii'))
    
    def set_depth_pid(self, p, i, d):
        payload = 'SDC' + str(p) + ',' + str(i) + ',' + str(d)
        self.ser.write(payload.encode('ascii'))
    
    def set_pitch_pid(self, p, i, d):
        payload = 'SDC' + str(p) + ',' + str(i) + ',' + str(d)
        self.ser.write(payload.encode('ascii'))
    
    def set_depth_calibration(self, p, i, d):
        payload = 'SD_trim'
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