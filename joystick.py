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
    
    trigger = pyqtSignal()
    
    power_factor = 0.5
    
    def __init__(self):
        QThread.__init__(self)
    
    def run(self):
        
        while(1):
            events = get_gamepad()
            for event in events:
                self.values[event.code] = event.state
            #print(event.ev_type, event.code, event.state)
            #print(self.values.values()
            
            self.thrustre_FL = self.power_factor * math.sin() + math.atan()
            self.thrustre_FR = self.power_factor * math.cos() - math.atan()
            self.thrustre_BR = self.power_factor * math.sin() + math.atan()
            self.thrustre_BL = self.power_factor * math.cos() - math.atan()
            
            self.thrustre_VF = 
            self.thrustre_VB = 
            
            
    def __del__(self):
        self.wait()        
    
    def stop(self):
        self._isRunning = False
        
if __name__ == '__main__':
    joy = joystick()
    joy.start()