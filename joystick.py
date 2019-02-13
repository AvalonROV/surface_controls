from PyQt5.QtCore import QThread, pyqtSignal
from inputs import get_gamepad
import math



class joystick(QThread):
    
    values = {
            "BTN_TL" : 0,
            "BTN_Tr" : 0,
            "BTN_START" : 0,
            "BTN_SELECT" : 0,
            "BTN_NORTH" : 0,
            "BTN_SOUTH" : 0,
            "BTN_EAST" : 0,
            "BTN_WEST" : 0,
            "ABS_X" : 0,
            "ABS_y" : 0,
            "ABS_RX" : 0,
            "ABS_RY" : 0,
            "ABS_Z" : 0,
            "ABS_RZ" : 0,
            "ABS_HAT0x" : 0,
            "ABS_HAT0Y": 0,
            }
    
    signal = pyqtSignal(dict)
    
    power_factor = 0.5
    
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        
    def run(self):
        self.running = True
        while self.running:
            try:
                events = get_gamepad()
                for event in events:
                    self.values[event.code] = event.state
                #print(event.ev_type, event.code, event.state)
                #print(self.values.values()
                
                
                self.signal.emit(self.values)
            except:
                pass
         
        print("Joystick thread terminating")
                   
if __name__ == '__main__':
    joy = joystick()
    joy.start()