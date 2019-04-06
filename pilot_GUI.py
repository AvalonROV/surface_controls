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
    
    power_factor = 1
    fwd_factor = 400*0.5
    side_factor = 400*0.5
    vertical_factor = 400    
    thrusters_power = [500]*6
    thrusters_names = ["fl" , "fr", "br", "bl", "vf", "vb"]
    '''
    Thrusters mapping:
        0 --> Front left
        1 --> Front right
        2 --> Back right
        3 --> Back left
        4 --> Vertical front
        5 --> Vertical back
    '''
        
    def __init__(self,surface):
        super(Window,self).__init__()
        self.setCentralWidget(ImageWidget(surface))
        loadUi('interface.ui',self)
        
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
        
        self.load_config_file()
        
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update_ui)
        self.refresh_timer.start(50)
        
        self.COMport_list.currentIndexChanged.connect(self.update_serial_COM_port)
        
        #Thrusters flip checkboxes change state defintion 
        self.FL_flip_checkbox.stateChanged.connect(lambda:self.flip_thruster_direction(self.FL_flip_chkbox, 0))
        self.FR_flip_checkbox.stateChanged.connect(lambda:self.flip_thruster_direction(self.FR_flip_chkbox, 1))
        self.BR_flip_checkbox.stateChanged.connect(lambda:self.flip_thruster_direction(self.BR_flip_chkbox, 2))
        self.BL_flip_checkbox.stateChanged.connect(lambda:self.flip_thruster_direction(self.BL_flip_chkbox, 3))
        self.VF_flip_checkbox.stateChanged.connect(lambda:self.flip_thruster_direction(self.VF_flip_chkbox, 4))
        self.VB_flip_checkbox.stateChanged.connect(lambda:self.flip_thruster_direction(self.VB_flip_chkbox, 5))
        
        #Thrusters ordering line-edit initialization 
        self.FL_order.editingFinished.connect(lambda:self.edit_thrusters_order(self.FL_order, 0))
        self.FR_order.editingFinished.connect(lambda:self.edit_thrusters_order(self.FR_order, 1))
        self.BR_order.editingFinished.connect(lambda:self.edit_thrusters_order(self.BR_order, 2))
        self.BL_order.editingFinished.connect(lambda:self.edit_thrusters_order(self.BL_order, 3))
        self.VF_order.editingFinished.connect(lambda:self.edit_thrusters_order(self.VF_order, 4))
        self.VB_order.editingFinished.connect(lambda:self.edit_thrusters_order(self.VB_order, 5))
       
        #Thrusters manual power input
        self.FL_manual_power.editingFinished.connect(self.manual_thrusters_control)
        self.FR_manual_power.editingFinished.connect(self.manual_thrusters_control)
        self.BR_manual_power.editingFinished.connect(self.manual_thrusters_control)
        self.BL_manual_power.editingFinished.connect(self.manual_thrusters_control)
        self.VF_manual_power.editingFinished.connect(self.manual_thrusters_control)
        self.VB_manual_power.editingFinished.connect(self.manual_thrusters_control)
        
        self.depth_tune_checkbox.stateChanged.connect(lambda:self.change_input_state(self.depth_tune_checkbox, "depth"))
        self.depth_enable_checkbox.stateChanged.connect(lambda:self.enable_controller(self.depth_enable_checkbox, "depth"))
        self.p_depth_gain_textbox.editingFinished.connect(lambda:self.change_controller_gains("depth"))
        self.i_depth_gain_textbox.editingFinished.connect(lambda:self.change_controller_gains("depth"))
        self.d_depth_gain_textbox.editingFinished.connect(lambda:self.change_controller_gains("depth"))
        #self.default_depth_controller_btn.clicked.connect(lambda:self.reset_controller_gains_to_default("depth"))
        
        self.pitch_tune_checkbox.stateChanged.connect(lambda:self.change_input_state(self.pitch_tune_checkbox, "pitch"))
        self.pitch_enable_checkbox.stateChanged.connect(lambda:self.enable_controller(self.pitch_enable_checkbox, "pitch"))
        self.p_pitch_gain_textbox.editingFinished.connect(lambda:self.change_controller_gains("pitch"))
        self.i_pitch_gain_textbox.editingFinished.connect(lambda:self.change_controller_gains("pitch"))
        self.d_pitch_gain_textbox.editingFinished.connect(lambda:self.change_controller_gains("pitch"))
        #self.default_pitch_controller_btn.clicked.connect(lambda:self.reset_controller_gains_to_default("pitch")) 
        
    def load_config_file(self):
        #Loading thrusters flip from config file
        self.config = configparser.ConfigParser()
        self.config.read('rov_config.ini')
        
        #loading directions from the config file
        self.thrusters_flip = []
        self.thrusters_flip.append(int(self.config['Directions']['fl'])) 
        self.thrusters_flip.append(int(self.config['Directions']['fr'])) 
        self.thrusters_flip.append(int(self.config['Directions']['br']))
        self.thrusters_flip.append(int(self.config['Directions']['bl'])) 
        self.thrusters_flip.append(int(self.config['Directions']['vf'])) 
        self.thrusters_flip.append(int(self.config['Directions']['vb']))
        
        #Intiallizing thruters flipping checkboxes
        self.FL_flip_checkbox.setChecked(False if self.thrusters_flip[0] == 1 else True)
        self.FR_flip_checkbox.setChecked(False if self.thrusters_flip[1] == 1 else True)
        self.BR_flip_checkbox.setChecked(False if self.thrusters_flip[2] == 1 else True)
        self.BL_flip_checkbox.setChecked(False if self.thrusters_flip[3] == 1 else True)
        self.VF_flip_checkbox.setChecked(False if self.thrusters_flip[4] == 1 else True)
        self.VB_flip_checkbox.setChecked(False if self.thrusters_flip[5] == 1 else True)
        
        #Initiallizing thrusters order
        self.thrusters_order = []
        self.thrusters_order.append(int(self.config['Order']['fl'])) 
        self.thrusters_order.append(int(self.config['Order']['fr'])) 
        self.thrusters_order.append(int(self.config['Order']['br']))
        self.thrusters_order.append(int(self.config['Order']['bl'])) 
        self.thrusters_order.append(int(self.config['Order']['vf'])) 
        self.thrusters_order.append(int(self.config['Order']['vb']))
        
        self.FL_order.setText(str(self.thrusters_order[0]))
        self.FR_order.setText(str(self.thrusters_order[1]))
        self.BR_order.setText(str(self.thrusters_order[2]))
        self.BL_order.setText(str(self.thrusters_order[3]))
        self.VF_order.setText(str(self.thrusters_order[4]))
        self.VB_order.setText(str(self.thrusters_order[5]))
        
        self.depth_enable_checkbox.setChecked(True if self.config['depth']['state'] == "1" else False)
        self.enable_controller(self.depth_enable_checkbox, "depth")
        self.p_depth_gain_textbox.setText(self.config['depth']['p'])
        self.i_depth_gain_textbox.setText(self.config['depth']['i'])
        self.d_depth_gain_textbox.setText(self.config['depth']['d'])
        
        self.pitch_enable_checkbox.setChecked(True if self.config['pitch']['state'] == "1" else False)
        self.enable_controller(self.pitch_enable_checkbox, "pitch")
        self.p_pitch_gain_textbox.setText(self.config['pitch']['p'])
        self.i_pitch_gain_textbox.setText(self.config['pitch']['i'])
        self.d_pitch_gain_textbox.setText(self.config['pitch']['d'])
        
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
            '''
            data = self.comms.get_telemetry()
        
            self.depth_label.setText(data["depth"])
            self.temp_label.setText(data["temprature"])
            self.ph_label.setText(data["ph"])
            self.pitch_angle_label.setText(data["pitch_angle"])
            self.roll_angle_label.setText(data["roll_angle"])
           ''' 
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
        
        if not self.manual_mode_checkbox.isChecked():
            pygame.event.pump()
            self.send_controls()
                
        self.FL_thruster_label.setText(str(self.thrusters_power[0]))
        self.FR_thruster_label.setText(str(self.thrusters_power[1]))
        self.BR_thruster_label.setText(str(self.thrusters_power[2]))
        self.BL_thruster_label.setText(str(self.thrusters_power[3]))
        self.VF_thruster_label.setText(str(self.thrusters_power[4]))
        self.VB_thruster_label.setText(str(self.thrusters_power[5]))
    
    def send_controls(self):
        try:
            self.LTX_Axis = self.my_joystick.get_axis(0)
            self.LTY_Axis = self.my_joystick.get_axis(1) * -1
            self.RTX_Axis = self.my_joystick.get_axis(4)
            self.RTY_Axis = self.my_joystick.get_axis(3) * -1
            self.vertical_power = self.my_joystick.get_axis(2)
            
            self.thrusters_power[0] = int(500 + (self.fwd_factor * self.RTY_Axis - self.side_factor * self.RTX_Axis) * self.power_factor * self.thrusters_flip[0]) #Front right
            self.thrusters_power[1] = int(500 + (self.fwd_factor * self.LTY_Axis + self.side_factor * self.LTX_Axis) * self.power_factor * self.thrusters_flip[1]) #Front left
            self.thrusters_power[2] = int(500 + (self.fwd_factor * self.LTY_Axis - self.side_factor * self.LTX_Axis) * self.power_factor * self.thrusters_flip[2]) #Back Left
            self.thrusters_power[3] = int(500 + (self.fwd_factor * self.RTY_Axis + self.side_factor * self.RTX_Axis) * self.power_factor * self.thrusters_flip[3]) #Back right
            self.thrusters_power[4] = int(500 + self.vertical_power * self.vertical_factor * self.power_factor * self.thrusters_flip[4]) #Vertical front
            self.thrusters_power[5] = int(500 + self.vertical_power * self.vertical_factor * self.power_factor * self.thrusters_flip[5]) #Vertical back
            
            string  = str(self.thrusters_power[self.thrusters_order.index(1)])
            string += str(self.thrusters_power[self.thrusters_order.index(2)])
            string += str(self.thrusters_power[self.thrusters_order.index(3)])
            string += str(self.thrusters_power[self.thrusters_order.index(4)])
            string += str(self.thrusters_power[self.thrusters_order.index(5)])
            string += str(self.thrusters_power[self.thrusters_order.index(6)])

            '''
            string = str(self.thrustre_BL)
            string +=str(self.thrustre_VF)
            string += str(self.thrustre_FL)
            string += str(self.thrustre_VB)
            string += str(self.thrustre_FR)
            string += str(self.thrustre_BR)
            '''
    
            state = self.comms.set_thrsuters(string)
            self.debug_response.append(">> " + state)
            
        except Exception  as e:
            self.debug_response.append("ERROR: " + str(e))
            #print("Joystick not connected LOL")
            self.joystick_connection_state=False
    
    def manual_thrusters_control(self):
        self.thrusters_power[0] = int(self.FL_manual_power.text()) #Front right
        self.thrusters_power[1] = int(self.FR_manual_power.text()) #Front left
        self.thrusters_power[2] = int(self.BR_manual_power.text()) #Back Left
        self.thrusters_power[3] = int(self.BL_manual_power.text()) #Back right
        self.thrusters_power[4] = int(self.VF_manual_power.text()) #Vertical front
        self.thrusters_power[5] = int(self.VB_manual_power.text()) #Vertical back
        
        string  = str(self.thrusters_power[self.thrusters_order.index(1)])
        string += str(self.thrusters_power[self.thrusters_order.index(2)])
        string += str(self.thrusters_power[self.thrusters_order.index(3)])
        string += str(self.thrusters_power[self.thrusters_order.index(4)])
        string += str(self.thrusters_power[self.thrusters_order.index(5)])
        string += str(self.thrusters_power[self.thrusters_order.index(6)])

        state = self.comms.set_thrsuters(string)
        #self.debug_response.append("Debug: power" + str(self.thrusters_power))
        #self.debug_response.append("Debug: order" + str(self.thrusters_order))
        self.debug_response.append(">> " + state)
    
    def edit_thrusters_order(self, thruster, thruster_number):            
        index = self.thrusters_order.index(int(thruster.text()))
        
        self.thrusters_order[index] = self.thrusters_order[thruster_number]
        self.thrusters_order[thruster_number] = int(thruster.text())
        
        self.FL_order.setText(str(self.thrusters_order[0]))
        self.FR_order.setText(str(self.thrusters_order[1]))
        self.BR_order.setText(str(self.thrusters_order[2]))
        self.BL_order.setText(str(self.thrusters_order[3]))
        self.VF_order.setText(str(self.thrusters_order[4]))
        self.VB_order.setText(str(self.thrusters_order[5]))
        
        self.config['Order'][self.thrusters_names[index]] = str(self.thrusters_order[index])
        self.config['Order'][self.thrusters_names[thruster_number]] = str( self.thrusters_order[thruster_number])
        with open('rov_config.ini', 'w') as configfile:
            self.config.write(configfile)
    
    def flip_thruster_direction(self, thruster, index):
        self.thrusters_flip[index] *= -1
        self.config['Directions'][self.thrusters_names[index]] = str(self.thrusters_flip[index])
        with open('rov_config.ini', 'w') as configfile:
            self.config.write(configfile)
    
    def change_input_state(self, checkbox, obj):
        if obj == "depth":
            self.p_depth_gain_textbox.setReadOnly(not checkbox.checkState())
            self.i_depth_gain_textbox.setReadOnly(not checkbox.checkState())
            self.d_depth_gain_textbox.setReadOnly(not checkbox.checkState())
        elif obj == "depth":
            self.p_pitch_gain_textbox.setReadOnly(not checkbox.checkState())
            self.i_pitch_gain_textbox.setReadOnly(not checkbox.checkState())
            self.d_pitch_gain_textbox.setReadOnly(not checkbox.checkState())
        elif obj == "thrusters":
            print(5)
       
    def enable_controller(self, checkbox, controller):
        if self.serial_commuincation_status:
            controller_state = checkbox.isChecked()
            return_state = self.comms.set_pid_controller_state(controller, str(int(controller_state )))
            self.debug_response.append(">> " + return_state) 
            
            self.config[controller]["state"] = str(int(controller_state ))
            with open('rov_config.ini', 'w') as configfile:
                self.config.write(configfile)
            
        else:
            self.debug_response.append("ERROR: Unable to enable controller, no comms available.")
            
    def change_controller_gains(self, controller):
        if self.serial_commuincation_status:
            if controller == "depth":
                return_state = self.comms.set_pid_controller_gains(
                        controller,
                        self.p_depth_gain_textbox.text(), 
                        self.i_depth_gain_textbox.text(), 
                        self.d_depth_gain_textbox.text())
                
                self.config[controller]["p"] = self.p_depth_gain_textbox.text() 
                self.config[controller]["i"] = self.i_depth_gain_textbox.text()
                self.config[controller]["d"] = self.d_depth_gain_textbox.text()
            elif controller == "pitch":
                return_state = self.comms.set_pid_controller_gains(
                        controller,
                        self.p_pitch_gain_textbox.text(), 
                        self.i_pitch_gain_textbox.text(), 
                        self.d_pitch_gain_textbox.text())
                
                self.config[controller]["p"] = self.p_pitch_gain_textbox.text()
                self.config[controller]["i"] = self.i_pitch_gain_textbox.text()
                self.config[controller]["d"] = self.d_pitch_gain_textbox.text()
            
            self.debug_response.append(">> " + return_state)
            
            with open('rov_config.ini', 'w') as configfile:
                self.config.write(configfile)
        else:
            self.debug_response.append("ERROR: Unable to chnage controller gains, no comms available.")
            
    '''      
    def reset_controller_gains_to_default(self, controller):
        if self.depth_edit_checkbox.isChecked() and self.serial_commuincation_status:
            self.comms.set_depth_pid(
                self.p_depth_gain_default, 
                self.i_depth_gain_default, 
                self.d_depth_gain_default)
            
            self.p_depth_gain.setText(self.p_depth_gain_default)
            self.i_depth_gain.setText(self.i_depth_gain_default)
            self.d_depth_gain.setText(self.d_depth_gain_default)
            '''
           
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
