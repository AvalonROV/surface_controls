import sys
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import QTimer
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage
import cv2




class Webcome(QDialog):
    screen = " ";
    screen1 = " ";

    def __init__(self):
        super(Webcome,self).__init__()
        loadUi('webcamera.ui',self)
        self.image = None
        self.startButton.clicked.connect(self.start_webcam)
        self.endButton.clicked.connect(self.stop_webcam)
        self.Front.clicked.connect(self.FrontA)
        self.Front_2.clicked.connect(self.FrontB)
        self.Back.clicked.connect(self.BackA)
        self.Back_2.clicked.connect(self.BackB)
       # self.Left.clicked.connect(self.LeftA)
       # self.Left_2.clicked.connect(self.LeftB)
       # self.Right.clicked.connect(self.RightA)
       # self.Right_2.clicked.connect(self.RightB)

    def start_webcam(self):
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT,500)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH,900)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5)

    def update_frame(self):
        ret,self.image=self.capture.read()  #takes Video capture
        self.image = cv2.flip(self.image, 1)
        self.displayImage(self.image, 1)


    def stop_webcam(self):
        self.timer.stop()

    def displayImage(self,img,window=1):
        qformat = QImage.Format_Indexed8
        if len(img.shape)== 3 : #[0] - rows,  [1] = columns , [2] - chanel less
          if img.shape[2]== 4 :
            qformat = QImage.Format_RGBA8888
          else:
            qformat = QImage.Format_RGB888

        outImage = QImage(img,img.shape[1],img.shape[0],img.strides[0],qformat)
        #BGR>>RGB
        outImage = outImage.rgbSwapped()

        if window == 1:
         self.MainDisplay.setPixmap(QPixmap.fromImage(outImage))
         self.MainDisplay.setScaledContents(True)
         self.MainDisplay_2.setPixmap(QPixmap.fromImage(outImage))
         self.MainDisplay_2.setScaledContents(True)

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
        global screen
        screen = "Front"

    def ChangeScreenF1 (self):
        global screen1
        screen1 = "Front"

    def ChangeScreenB (self) :
        global screen
        screen = "Back"

    def ChangeScreenB1 (self):
        global screen1
        screen1 = "Back"











   # def LeftA (self):


  #  def LeftB (self):


  #  def RightA (self):


   # def RightB (self):

        #self.Front_2.hide()
       # self.Right.show()
       # self.Left.show()
       # self.Back.show()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Webcome()
    window.setWindowTitle("Avalon Graphical Interface");
    window.show()
    window.showFullScreen()
    sys.exit(app.exec_())
