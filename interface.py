import sys
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import QTimer
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage
import cv2
import serial_com




class Webcome(QDialog):
    screen = " ";
    screen1 = " ";

    def __init__(self):
        self.noob = "";
        self.camera = 0;
        super(Webcome,self).__init__()
        loadUi('webcamera.ui',self)
        self.image = None

        self.Arduino.clicked.connect(self.Arduino1)
        self.startButton.clicked.connect(self.start_webcam)
        self.endButton.clicked.connect(self.stop_webcam)
        self.Front.clicked.connect(self.FrontA)
        self.Front_2.clicked.connect(self.FrontB)
        self.Back.clicked.connect(self.BackA)
        self.Back_2.clicked.connect(self.BackB)
       # self.Left.clicked.connect(self.LeftA)
    #        # self.Left_2.clicked.connect(self.LeftB)
    #        # self.Right.clicked.connect(self.RightA)
    #        # self.Right_2.clicked.connect(self.RightB)

    def start_webcam(self):
        self.capture = cv2.VideoCapture(self.camera)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(6)

    def update_frame(self):
        ret,self.image = self.capture.read()
        self.image = cv2.flip(self.image, 1)
        self.displayImage(self.image)


    def stop_webcam(self):
        self.timer.stop()

    def displayImage(self,img,window=1):
        qformat = QImage.Format_Indexed8
        if len(img.shape)== 3 :
          if img.shape[2]== 4 :
            qformat = QImage.Format_RGBA8888
          else:
            qformat = QImage.Format_RGB888

        outImage = QImage(img,img.shape[1],img.shape[0],img.strides[0],qformat)
        outImage = outImage.rgbSwapped()

        if window == 1:
         self.MainDisplay.setPixmap(QPixmap.fromImage(outImage))
         self.MainDisplay.setScaledContents(True)
         #self.MainDisplay_2.setPixmap(QPixmap.fromImage(outImage))
         #self.MainDisplay_2.setScaledContents(True)

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

    def Arduino1(self):



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Webcome()
    window.setWindowTitle("Avalon Graphical Interface");
    window.show()
    sys.exit(app.exec_())
