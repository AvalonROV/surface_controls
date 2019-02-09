import serial
import serial.tools.list_ports as ls_port
import sys 

def ls_COMports():
    return [comport.device for comport in serial.tools.list_ports.comports()]

class SerialComms:
    """
    ........................
    port  --> COM(X) for windows systems, dev/tty/USB(X) for linux based system
    baud_rate ---> {9600, 152000.. etc}
    
    """
    #intialize pySerial
    def __init__(self, port, baud_rate = 9600):
    
        self.ser = serial.Serial(port, baudrate = baud_rate, timeout = 1)
        
    def end_comms(self):
        self.ser.close()
    
    def getPotentiometerValues(self):
        self.ser.write('g'.encode('ascii'))
        arduinoData = self.ser.readline().strip().decode('ascii')
        return arduinoData
    
    def getThrusterValues(self):
        
        self.ser.write('T'.encode('ascii'))
        for i in range(5):  
            arduinoData = self.ser.readline().strip().decode('ascii')
            return arduinoData
    
    def getSingleThrusterValue(self, num = 0):
        self.ser.write('s'.encode('ascii'))

if __name__ == "__main__":
    comms = SerialComms('COM6')
    while(1):
        try:
            print(comms.getPotentiometerValues())
        except:
            comms.end_comms()
            print("Port cLosed!")
            sys.exit()