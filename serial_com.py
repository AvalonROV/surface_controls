class SerialComms:
    """
    ........................
    port  --> COM(X) for windows systems, dev/tty/USB(X) for linux based system
    baud_rate ---> {9600, 152000.. etc}
    
    """
    import serial
    #intialize pySerial
    def __init__(self, port, baud_rate = 9600):
        
        self.port = port
        self.baud_rate = baud_rate
        self.ser = serial.Serial(port, baudrate = baud_rate, timeout = 1)
        
    #Test function for potentiometer   
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


        
while(1):
    Comms = SerialComms('COM3')
    print(" To get speed --> enter 'v' \n To get thruster values --> 'T'")
    userInput = input("Enter char")