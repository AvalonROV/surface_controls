from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage, QPainter
import configparser
import ROV_comms
import pygame
import time
import sys
import cv2

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

class ImageWidget(QWidget): #For pygame object to have the joystick running
    def __init__(self,surface,parent=None):
        super(ImageWidget,self).__init__(parent)
        w=surface.get_width()
        h=surface.get_height()
        self.data=surface.get_buffer().raw
        self.image=QImage(self.data,w,h,QImage.Format_RGB32)

    def paintEvent(self,event):
        qp=QPainter()
        qp.begin(self)
        qp.drawImage(0,0,self.image)
        qp.end()

def joystick_available():
    pygame.event.get()
    if pygame.joystick.get_count() >= 1:
        return True
    else:
        return False 

class Window(QMainWindow):
    def __init__(self,surface):
        super(Window,self).__init__()
        self.setCentralWidget(ImageWidget(surface))
        loadUi('interface.ui',self)
        
        self.load_variables()
        
        self.serial_commuincation_status = False
        self.comms = ROV_comms.Serial()
        self.ls_COM_ports_thread = ROV_comms.ls_COM_ports()
        self.ls_COM_ports_thread.signal.connect(self.update_COMport_list)
        self.ls_COM_ports_thread.start()
        self.ports_list = []
        
        self.feed_1 = get_video_feed(0)
        self.feed_1.signal.connect(self.display_feed_1)
        #self.feed_1.start()
        
        self.feed_2 = get_video_feed(1)
        self.feed_2.signal.connect(self.display_feed_2)
        #self.feed_2.start()
        
        try:
            self.my_joystick = pygame.joystick.Joystick(0)
            self.my_joystick.init()
            self.joystick_connection_state = True
        except:
            print("Joystick not connected")
            self.joystick_connection_state = False
        
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update_ui)
        self.refresh_timer.start(50)
        
        self.COMport_list.currentIndexChanged.connect(self.update_serial_COM_port)
        
        self.depth_enable_checkbox.stateChanged.connect(self.enable_depth_controller)
        self.update_depth_controller_btn.clicked.connect(self.set_depth_gains_to_update)
        self.default_depth_controller_btn.clicked.connect(self.set_depth_gains_to_default)
        
        self.pitch_enable_checkbox.stateChanged.connect(self.enable_pitch_controller)
        self.update_pitch_controller_btn.clicked.connect(self.set_pitch_gains_to_update)
        self.default_pitch_controller_btn.clicked.connect(self.set_pitch_gains_to_default)
        
        self.flip_FL_btn.clicked.connect(self.flip_FL_function)
        self.flip_FR_btn.clicked.connect(self.flip_FR_function)
        self.flip_BR_btn.clicked.connect(self.flip_BR_function)
        self.flip_BL_btn.clicked.connect(self.flip_BL_function)
        self.flip_VF_btn.clicked.connect(self.flip_VF_function)
        self.flip_VB_btn.clicked.connect(self.flip_VB_function)
                
    def load_variables(self):
        self.config = configparser.ConfigParser()
        self.config.read('rov_config.ini')
        
        self.FL_flip = int(self.config['Directions']['FL'])
        self.FR_flip = int(self.config['Directions']['FR'])
        self.BR_flip = int(self.config['Directions']['BR'])
        self.BL_flip = int(self.config['Directions']['BL'])
        self.VF_flip = int(self.config['Directions']['VF'])
        self.VB_flip = int(self.config['Directions']['VB'])
        
        self.power_factor = 1
        self.fwd_factor = 400*0.5
        self.side_factor = 400*0.5
        self.vertical_factor = 400
        self.thrustre_FL = 1500
        self.thrustre_BL = 1500
        self.thrustre_FR = 1500
        self.thrustre_BR = 1500            
        self.thrustre_VF = 1500
        self.thrustre_VB = 1500
    
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
            
    def update_serial_COM_port(self):
        if str(self.COMport_list.currentText()) != "":
           self.comms.update_port(str(self.COMport_list.currentText()))
           self.serial_commuincation_status = True
           print("Connected to: " + str(self.COMport_list.currentText()))
           
    def update_ui(self):
        if self.serial_commuincation_status:
            data = self.comms.get_telemetry()
            self.depth_label.setText(data["depth"])
            self.temp_label.setText(data["temprature"])
            self.ph_label.setText(data["ph"])
            self.pitch_angle_label.setText(data["pitch_angle"])
            self.roll_angle_label.setText(data["roll_angle"])
            
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
        
        if self.joystick_connection_state:
            self.joystick_state_label.setText("Connected")
            self.joystick_state_label.setStyleSheet('''background-color: green;
                                                  color: rgba(0,190,255,255);
                                                  border-style: solid;
                                                  border-radius: 3px;
                                                  border-width: 0.5px;
                                                  border-color:rgba(0,140,255,255);''')
        else:
            self.joystick_state_label.setText("Not connected")
            self.joystick_state_label.setStyleSheet('''background-color: red;
                                                  color: rgba(0,190,255,255);
                                                  border-style: solid;
                                                  border-radius: 3px;
                                                  border-width: 0.5px;
                                                  border-color:rgba(0,140,255,255);''')
            
        pygame.event.pump()
        self.send_controls()
        
        self.FL_thruster_label.setText(str(self.thrustre_FL))
        self.FR_thruster_label.setText(str(self.thrustre_FR))
        self.BR_thruster_label.setText(str(self.thrustre_BR))
        self.BL_thruster_label.setText(str(self.thrustre_BL))
        self.VF_thruster_label.setText(str(self.thrustre_VF))
        self.VB_thruster_label.setText(str(self.thrustre_VB))
    
    def send_controls(self):
        try:
            self.LTX_Axis = self.my_joystick.get_axis(0)
            self.LTY_Axis = self.my_joystick.get_axis(1) * -1
            self.RTX_Axis = self.my_joystick.get_axis(4)
            self.RTY_Axis = self.my_joystick.get_axis(3) * -1
            self.vertical_power = self.my_joystick.get_axis(2)
            
            self.thrustre_FL = int(1500 + (self.fwd_factor * self.LTY_Axis + self.side_factor * self.LTX_Axis) * self.power_factor * self.FL_flip)
            self.thrustre_BL = int(1500 + (self.fwd_factor * self.LTY_Axis - self.side_factor * self.LTX_Axis) * self.power_factor * self.BL_flip)
            
            self.thrustre_FR = int(1500 + (self.fwd_factor * self.RTY_Axis - self.side_factor * self.RTX_Axis) * self.power_factor * self.FR_flip)
            self.thrustre_BR = int(1500 + (self.fwd_factor * self.RTY_Axis + self.side_factor * self.RTX_Axis) * self.power_factor * self.BR_flip)
            
            self.thrustre_VF = int(1500 + self.vertical_power * self.vertical_factor * self.power_factor * self.VF_flip)
            self.thrustre_VB = int(1500 + self.vertical_power * self.vertical_factor * self.power_factor * self.VB_flip)
            
            string = "ST1" + str(self.thrustre_FL) 
            string += "2" + str(self.thrustre_VF)
            string += "3" + str(self.thrustre_FR)
            string += "4" + str(self.thrustre_BR)
            string += "5" + str(self.thrustre_VB)
            string += "6" + str(self.thrustre_BL)
            
            self.debug_response.setText(string)
        except:
            print("Joystick not connected")
            self.joystick_connection_state=False
            
    def flip_FL_function(self):
        if self.edit_thruster_checkbox.isChecked():
            self.FL_flip *= -1
            self.config['Directions']['FL'] = str(self.FL_flip)
            with open('rov_config.ini', 'w') as configfile:
                self.config.write(configfile)
        
    def flip_FR_function(self):
        if self.edit_thruster_checkbox.isChecked():
            self.FR_flip *= -1
            self.config['Directions']['FR'] = str(self.FR_flip)
            with open('rov_config.ini', 'w') as configfile:
                self.config.write(configfile)
            
    def flip_BR_function(self):
        if self.edit_thruster_checkbox.isChecked():
            self.BR_flip *= -1
            self.config['Directions']['BR'] = str(self.BR_flip)
            with open('rov_config.ini', 'w') as configfile:
                self.config.write(configfile)
        
    def flip_BL_function(self):
        if self.edit_thruster_checkbox.isChecked():
            self.BL_flip *= -1
            self.config['Directions']['BL'] = str(self.BL_flip)
            with open('rov_config.ini', 'w') as configfile:
                self.config.write(configfile)
        
    def flip_VF_function(self):
        if self.edit_thruster_checkbox.isChecked():
            self.VF_flip *= -1
            self.config['Directions']['VF'] = str(self.VF_flip)
            with open('rov_config.ini', 'w') as configfile:
                self.config.write(configfile)
        
    def flip_VB_function(self):
        if self.edit_thruster_checkbox.isChecked():
            self.VB_flip *= -1
            self.config['Directions']['VB'] = str(self.VB_flip)
            with open('rov_config.ini', 'w') as configfile:
                self.config.write(configfile)
        
    def enable_depth_controller(self):
        if self.serial_commuincation_status:
            state = self.depth_edit_checkbox.isChecked()
            self.comms.set_depth_pid_state(str(int(state)))
    
    def enable_pitch_controller(self):
        if self.serial_commuincation_status:
            state = self.pitch_edit_checkbox.isChecked()
            self.comms.set_pitch_pid_state(str(int(state)))
    
    def set_depth_gains_to_update(self):
        if self.depth_edit_checkbox.isChecked() and self.serial_commuincation_status:
            self.comms.set_depth_pid(
                self.p_depth_gain.text(), 
                self.i_depth_gain.text(), 
                self.d_depth_gain.text())
            
    def set_depth_gains_to_default(self):
        if self.depth_edit_checkbox.isChecked() and self.serial_commuincation_status:
            self.comms.set_depth_pid(
                self.p_depth_gain_default, 
                self.i_depth_gain_default, 
                self.d_depth_gain_default)
            
            self.p_depth_gain.setText(self.p_depth_gain_default)
            self.i_depth_gain.setText(self.i_depth_gain_default)
            self.d_depth_gain.setText(self.d_depth_gain_default)
                
    def set_pitch_gains_to_update(self):
        if self.pitch_edit_checkbox.isChecked() and self.serial_commuincation_status:
            self.comms.set_pitch_pid(
                self.p_pitch_gain.text(), 
                self.i_pitch_gain.text(), 
                self.d_pitch_gain.text())
    def set_pitch_gains_to_default(self):
        if self.pitch_edit_checkbox.isChecked() and self.serial_commuincation_status:            
            self.comms.set_depth_pid(
                self.p_pitch_gain_default, 
                self.i_pitch_gain_default, 
                self.d_pitch_gain_default)
            
            self.p_pitch_gain.setText(self.p_pitch_gain_default)
            self.i_pitch_gain.setText(self.i_pitch_gain_default)
            self.d_pitch_gain.setText(self.d_pitch_gain_default)
    
    def closeEvent(self, event):
        print( "Exiting application...")
        
        #self.joystick_thread.running = False
        self.ls_COM_ports_thread.running = False
        self.refresh_timer.stop()
        try:
            self.feed_1.end_feed()
        except:
            pass
        try:
            self.feed_2.end_feed()
        except:
            pass
        
        if self.serial_commuincation_status == True:
            self.comms.end_comms()
        pygame.quit ()
        event.accept()

pygame.init()
pygame.joystick.init()
s=pygame.Surface((640,480))

s.fill((64,128,192,224))

pygame.draw.circle(s,(255,100,10,255),(0,0),10)
app = QApplication(sys.argv)
GUI_window = Window(s)
GUI_window.show()
sys.exit(app.exec_())
