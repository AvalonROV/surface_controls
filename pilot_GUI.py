import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage   
import cv2
import joystick
import ROV_comms
import time

class get_video_feed(QThread):
    
    signal = pyqtSignal(QImage)
    
    def __init__(self, channel, parent=None):
        QThread.__init__(self, parent)
        self.channel = channel
    
    def run(self):
        self.capture = cv2.VideoCapture(self.channel) 
        
        self.running = True
        while self.running:
            ret, frame = self.capture.read()
        
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                #frame = cv2.flip(frame, 1)
                image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
                
                self.signal.emit(image)
            time.sleep(0.04)
    
    def end_feed(self):
        self.running = False
        self.capture.release()
        print("Camera feed on channel " + str(self.channel) + " closed")
    

class Window(QMainWindow):
    def __init__(self):
        super(Window,self).__init__()
        loadUi('interface.ui',self)
        
        self.ui_init()
        
        self.feed_1 = get_video_feed(0)
        self.feed_1.signal.connect(self.display_feed_1)
        self.feed_1.start()
        
        self.feed_2 = get_video_feed(1)
        self.feed_2.signal.connect(self.display_feed_2)
        self.feed_2.start()
        
        self.serial_commuincation_status = False
        self.start_serial_coms()
        
        self.Joystick_status = False
        self.joystick_thread = joystick.joystick()
        self.joystick_thread.signal.connect(self.send_data)
        self.joystick_thread.start()
        
        self.show()
        
    def ui_init(self):
        
        self.COMport_droplist_init()
        self.COMport_list.currentIndexChanged.connect(self.start_serial_coms)
        '''
        self.Front.clicked.connect(self.FrontA)
        self.Front_2.clicked.connect(self.FrontB)
        self.Back.clicked.connect(self.BackA)
        self.Back_2.clicked.connect(self.BackB)
        #self.Arduino.clicked.connect(self.Arduino1)
        '''
        #self.comms = serial_com.SerialComms('COM6')                
    
    def closeEvent(self, event):
        print( "Exiting application...")
        
        try:
            self.joystick_thread.running = False
        except:
            pass
        
        self.COMport_timer.stop()
        
        self.feed_1.end_feed()
        self.feed_2.end_feed()
        
        if self.serial_commuincation_status == True:
            self.comms.end_comms()
        
        event.accept()
        #sys.exit()
        
    def display_feed_1(self, image):
        try:
            self.MainDisplay.setPixmap(QPixmap.fromImage(image))
            self.MainDisplay.setScaledContents(True)
        except:
            print("No feed avaliable for Display 1")
    
    def display_feed_2(self, image):
        try:
            self.MainDisplay_2.setPixmap(QPixmap.fromImage(image))
            self.MainDisplay_2.setScaledContents(True)
        except:
            print("No feed avaliable for Display 2")
    
    def COMport_droplist_init(self):
        self.ports_list = ROV_comms.ls_COMports()
        self.COMport_list.addItems(self.ports_list)
        
        self.COMport_timer = QTimer(self)
        self.COMport_timer.timeout.connect(self.update_COMport_list)
        self.COMport_timer.start(50)
    
    def update_COMport_list(self):
        new_ports_list = ROV_comms.ls_COMports()
        
        if self.ports_list != new_ports_list:
            for port in new_ports_list: #Adding new ports
                if port not in self.ports_list:
                    self.COMport_list.addItem(port)
                    
            for index in range(len(self.ports_list)): #Deleting removed ports
                if self.ports_list[index] not in new_ports_list:
                    self.COMport_list.removeItem(index)
            
            self.ports_list = new_ports_list
    
    def start_serial_coms(self):
        if self.serial_commuincation_status == True:
            self.comms.end_comms()
        try:
            self.comms = ROV_comms.SerialComms(str(self.COMport_list.currentText()))
            print("Connected to: " + str(self.COMport_list.currentText()))
            
        except:
            pass
        
    def send_data(self, data):
       print(data.values())
       '''
        self.thrustre_FL = self.power_factor * math.sin() + math.atan()
        self.thrustre_FR = self.power_factor * math.cos() - math.atan()
        self.thrustre_BR = self.power_factor * math.sin() + math.atan()
        self.thrustre_BL = self.power_factor * math.cos() - math.atan()
        
        self.thrustre_VF = 0
        self.thrustre_VB = 0
        '''    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI_window = Window()
    sys.exit(app.exec_())
