import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage   
import cv2
import joystick
import ROV_comms
import time
import math

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
        
        self.serial_commuincation_status = False
        self.comms = ROV_comms.Serial()
        self.ls_COM_ports_thread = ROV_comms.ls_COM_ports()
        self.ls_COM_ports_thread.signal.connect(self.update_COMport_list)
        self.ls_COM_ports_thread.start()
        self.ports_list = []
        
        self.feed_1 = get_video_feed(0)
        self.feed_1.signal.connect(self.display_feed_1)
        self.feed_1.start()
        
        self.feed_2 = get_video_feed(1)
        self.feed_2.signal.connect(self.display_feed_2)
        self.feed_2.start()
        
        self.Joystick_status = False
        self.joystick_thread = joystick.joystick()
        self.joystick_thread.signal.connect(self.send_controls)
        self.joystick_thread.start()

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update_ui)
        self.refresh_timer.start(50)
        
        self.COMport_list.currentIndexChanged.connect(self.update_serial_COM_port)
        
        self.show()              
        
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
    
    def update_COMport_list(self, new_ports_list):
        if str(self.COMport_list.currentText()) not in new_ports_list:
            self.serial_commuincation_status = False
            
        if self.ports_list != new_ports_list:
            for port in new_ports_list: #Adding new ports
                if port not in self.ports_list:
                    self.COMport_list.addItem(port)
                        
            for index in range(len(self.ports_list)): #Deleting removed ports
                if self.ports_list[index] not in new_ports_list:
                    self.COMport_list.removeItem(index)
                
            self.ports_list = new_ports_list

    def update_ui(self):
        '''
        self.FL_thruster_label.setText(self.thrustre_FL)
        self.FR_thruster_label.setText(self.thrustre_FR)
        self.BR_thruster_label.setText(self.thrustre_BR)
        self.BL_thruster_label.setText(self.thrustre_BL)
        self.VF_thruster_label.setText(self.thrustre_VF)
        self.VB_thruster_label.setText(self.thrustre_VB)
        '''
        if self.serial_commuincation_status:
            self.serial_state_label.setText("Connected")
            self.serial_state_label.setStyleSheet('''background-color: green;
                                                  color: rgba(0,190,255,255);
                                                  border-style: solid;
                                                  border-radius: 3px;
                                                  border-width: 0.5px;
                                                  border-color:rgba(0,140,255,255);''')
        else:
            self.serial_state_label.setText("Not connected")
            self.serial_state_label.setStyleSheet('''background-color: red;
                                                  color: rgba(0,190,255,255);
                                                  border-style: solid;
                                                  border-radius: 3px;
                                                  border-width: 0.5px;
                                                  border-color:rgba(0,140,255,255);''')
        
        telemtry_data = "Telemetry:\n"
        telemtry_data += "Depth: " + str(1.24) + "m\n" 
        telemtry_data += "Temprature: " + str(21.2) + "C\n"
        telemtry_data += "pH: " + str(7.12)
        
        self.telemetry_label.setText(telemtry_data)
           
    def update_serial_COM_port(self):
        if str(self.COMport_list.currentText()) != "":
           self.comms.update_port(str(self.COMport_list.currentText()))
           self.serial_commuincation_status = True
           print("Connected to: " + str(self.COMport_list.currentText()))
        
    def send_controls(self, data):
        print(data["ABS_X"], data["ABS_Y"], data["ABS_RX"], data["ABS_RY"])
       
        '''
        self.thrustre_FL = 1500 + self.FL_flip + self.power_factor * math.sin() + math.atan()
        self.thrustre_FR = 1500 + self.FR_flip + self.power_factor * math.cos() - math.atan()
        self.thrustre_BR = 1500 + self.BR_flip + self.power_factor * math.sin() + math.atan()
        self.thrustre_BL = 1500 + self.BL_flip + self.power_factor * math.cos() - math.atan()
        
        sel1f.thrustre_VF = 1500 + self.VF_flip + 
        self.thrustre_VB = 1500 + self.VB_flip + 
        '''
    def closeEvent(self, event):
        print( "Exiting application...")

        self.joystick_thread.running = False
        self.ls_COM_ports_thread.running = False
        self.refresh_timer.stop()        
        self.feed_1.end_feed()
        self.feed_2.end_feed()
        
        if self.serial_commuincation_status == True:
            self.comms.end_comms()
        
        event.accept()
        #sys.exit()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI_window = Window()
    sys.exit(app.exec_())
