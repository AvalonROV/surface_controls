import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog
from PyQt5.QtCore import QTimer, QThread
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage   
import cv2
import serial_com

class get_video_feed(QThread):
    def __init__(self, channel):
        QThread.__init__(self)
        self.channel = channel
               
        
    def get_new_frame(self):
        ret, frame = self.capture.read()
        
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            #frame = cv2.flip(frame, 1)
            image = QImage(frame, frame.shape[1], frame.shape[0], 
                           frame.strides[0], QImage.Format_RGB888)
        else:
            image = None
        return ret, image
    
    def run(self):
        self.capture = cv2.VideoCapture(self.channel) 
        #self.get_new_frame()
    
    def __del__(self):
        self.wait()
    
    def end_feed(self):
        self.capture.release()
        print("Camera feed on channel " + str(self.channel) + " closed")
    
class Window(QMainWindow):
    def __init__(self):
        super(Window,self).__init__()
        loadUi('webcamera.ui',self)
        self.setWindowTitle("Avalon Graphical Interface");
        '''
        self.Front.clicked.connect(self.FrontA)
        self.Front_2.clicked.connect(self.FrontB)
        self.Back.clicked.connect(self.BackA)
        self.Back_2.clicked.connect(self.BackB)
        #self.Arduino.clicked.connect(self.Arduino1)
        '''
        
        #self.comms = serial_com.SerialComms('COM6')        
        
        self.show()
        self.display_feed(1, 2)
        
    def closeEvent(self, event):
        print( "Exiting application...")
        self.timer.stop()
        self.video_1.end_feed()
        self.video_2.end_feed()
        #self.comms.end_comms()
        event.accept()
        #sys.exit()

    def display_feed(self, channel_1, channel_2):
        self.video_1 = get_video_feed(channel_1)
        self.video_1.start()
        
        self.video_2 = get_video_feed(channel_2)
        self.video_2.start()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(50)
        
    def update_frame(self):
        try:
            state, image = self.video_1.get_new_frame()
            if state == True:
                self.MainDisplay.setPixmap(QPixmap.fromImage(image))
                self.MainDisplay.setScaledContents(True)
            else:
                print("No feed avaliable for Display 1")
            
            state, image = self.video_2.get_new_frame()
            if state == True:
                self.MainDisplay_2.setPixmap(QPixmap.fromImage(image))
                self.MainDisplay_2.setScaledContents(True)
            else:
                print("No feed avaliable for Display 2")
        except:
            pass
        
    '''    
    def FrontA (self):
        self.ChangeScreenF()
        if "Front" == screen :
           print(screen)
           self.Front_2.hide()
           self.Back.show()
           self.Back_2.show()

    def FrontB (self):
        self.ChangeScreenF1()
        if "Front" == screen1 :
           print(screen1)
           self.Front.hide()
           self.Back.show()
           self.Back_2.show()

    def BackA (self):
        self.ChangeScreenB()
        if "Back" == screen :
            print(screen)
            self.Back_2.hide()
            self.Front.show()
            self.Front_2.show()

    def BackB (self):
        self.ChangeScreenB1()
        if "Back" == screen1 :
            print(screen1)
            self.Back.hide()
            self.Front.show()
            self.Front_2.show()

    def ChangeScreenF (self):
        self.camera = 0;
        global screen
        screen = "Front"
        self.timer.stop()
        self.start_webcam()

    def ChangeScreenF1 (self):
        global screen1
        screen1 = "Front"

    def ChangeScreenB (self) :
        self.camera = 1;
        global screen
        screen = "Back"
        self.start_webcam()

    def ChangeScreenB1 (self):
        global screen1
        screen1 = "Back"
    '''
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI_window = Window()
    sys.exit(app.exec_())
