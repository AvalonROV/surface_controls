#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 22:36:36 2019
@author: Marwan Taher 
"""
import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
import math
import numpy as np

class LineFollow(QThread):
    signal = pyqtSignal(list)
    
    def __init__(self, parent=None, flip=1):
        QThread.__init__(self, parent)
        self.running = True
        self.flip = flip
        self.new_frame_available = False
    
    def get_new_frame(self, frame, ret):
        self.new_frame = frame
        self.new_ret = ret
        self.new_frame_available = True
    
    def stop(self):
        self.running = False
    
    def run(self):
        depth = 60
        width = 80
        
        x_centre = 320 # Contour x centre
        y_centre = 240 # Contour y centre
        
        current_direction = -1
        
        tracking_x_offset = 40
        tracking_y_offset = 40
        
        horizontal_motion = -1
        vetical_motion = -1
        
        directions = ["Top", "Right", "Bottom", "Left"]
        
        while self.running:
            if self.new_frame_available:
                self.new_frame_available = False
                
                ret, main_frame = self.new_ret, self.new_frame
                
                #----Slicing the frame ino 4 parts----------------------------#
                
                cropped_frame = [
                        main_frame [0:depth, x_centre-width:x_centre+width], #Top
                        main_frame [y_centre-width:y_centre+width, 639-depth:639], #Right
                        main_frame [479-depth:479, x_centre-width:x_centre+width], #Bottom
                        main_frame [y_centre-width:y_centre+width, 0:depth] #Left
                        ]
                
                #----Displaying some lines------------------------------------#
                cv2.line(main_frame, (320,0), (320, 480), (0, 0, 255), 2) #Vertical Line in the middle
                cv2.line(main_frame, (0,240), (640, 240), (0, 0, 255), 2) #Horizontal Line in the middle
                cv2.line(main_frame, (x_centre,0), (x_centre, 480), (0, 240, 0), 2) 
                cv2.line(main_frame, (0,y_centre), (640, y_centre), (0, 240, 0), 2)
                
                
#                cv2.imshow("Top",cropped_frame[0])
#                cv2.imshow("Right", cropped_frame[1])
#                cv2.imshow("Bottom", cropped_frame[2])
#                cv2.imshow("Left", cropped_frame[3])
    
                #----Looking for contours in the 4 cropped sections-----------#
                for x in range(4):        
                    gray = cv2.cvtColor(cropped_frame[x], cv2.COLOR_BGR2GRAY)
                    blur = cv2.GaussianBlur(gray, (5, 5), 0) 
                    ret, thresh = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY_INV)
                    contours, hierarchy = cv2.findContours(thresh, 1 , cv2.CHAIN_APPROX_NONE)
            
                    if len(contours) > 0:
                        cv2.drawContours(cropped_frame[x], contours, -1, (0, 100, 0), 2)
                        if current_direction == -1:
                            current_direction = x
                            break   
                        
                        if current_direction +2 != x and current_direction-2 != x:
                            current_direction = x
                            #print("Triggered: " + directions[current_direction])
                            c = max(contours, key=cv2.contourArea)
                            break    
                
                if current_direction == 0: #Top
                    vetical_motion = "Up"
                    x_centre = 320
                    y_centre = 80
                    
                elif current_direction == 1: #Right
                    horizontal_motion = "Right"
                    x_centre = 559
                    y_centre = 240
                    
                elif current_direction == 2: #Bottom
                    vetical_motion = "Down"
                    x_centre = 320
                    y_centre = 399
                    
                elif current_direction == 3: #Left
                    horizontal_motion = "Left"
                    x_centre = 80
                    y_centre = 240
              
                #----Correcting robot's side drift----------------------------#
                try:
                    M = cv2.moments(c)
                    COG_x_coordinate = int(M['m10'] /M['m00'])  #take x middle coordinate
                    COG_y_coordinate = int(M['m01'] / M['m00'])  #take y middle coordinates
                                
#                    cv2.line(main_frame, (COG_x_coordinate,0), (COG_x_coordinate, 480), (100, 160, 0), 2) 
#                    cv2.line(main_frame, (0,COG_y_coordinate), (640, COG_y_coordinate), (100, 160, 0), 2)
#                    print(COG_x_coordinate, COG_y_coordinate)
                    
                    if current_direction == 0 or current_direction == 2: #When in vertical motion
                        if COG_x_coordinate > width + tracking_x_offset:
                            horizontal_motion = "D_Right"
                            self.thruster_power = [1600,1300,1600, 1300]
                        elif COG_x_coordinate < width - tracking_x_offset:
                            horizontal_motion = "D_Left" 
                            self.thruster_power = [1300,1600,1300, 1600]
                        else:
                            horizontal_motion = "D_on track"
                            self.thruster_power = [1500,1500,1500, 1500]
                        
                    elif current_direction == 1 or current_direction == 3: #When in horizontal motion
                        if COG_y_coordinate < depth + tracking_y_offset:
                            vetical_motion = "D_Up"
                            self.thruster_power += [1600, 1600]
                        elif COG_y_coordinate > y_centre - tracking_y_offset:
                            vetical_motion = "D_Down"
                            self.thruster_power += [1400, 1400]
                        else:
                            vetical_motion = "D_on track"
                            self.thruster_power += [1500, 1500]
                    
                    self.thruster_power = [a*b for a,b in zip(self.thruster_power,self.thruster_flip)]
                    
                except Exception  as e:
                    print(e)
                
                # printing outcome
                print(vetical_motion, horizontal_motion)
                #cv2.imshow("Main_frame", main_frame)
                
                #----Crack length measurment----------------------------------#
                hsv = cv2.cvtColor(main_frame, cv2.COLOR_BGR2HSV) 
                lower_red = np.array([110,50,50]) 
                upper_red = np.array([130,255,255]) 
                  
                # Here we are defining range of bluecolor in HSV 
                # This creates a mask of blue coloured  
                # objects found in the frame. 
                mask = cv2.inRange(hsv, lower_red, upper_red) 
                
                contours, hierarchy = cv2.findContours(mask, 1 , cv2.CHAIN_APPROX_NONE)
                
                if len(contours) > 0:
                    cv2.drawContours(cropped_frame[x], contours, -1, (0, 100, 0), 2)
                    
                    c = max(contours, key=cv2.contourArea)
                    x,y,w,h = cv2.boundingRect(c)
                    cv2.rectangle(main_frame,(x,y),(x+w,y+h),(0,255,0),2)
                    
                    if w > h:
                        crack_length = (w*1.8) / h
                    else:
                        crack_length = (h*1.8) / w
                    
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(main_frame,"Crack length = " + str(crack_length) + "cm",(72,45), font, 1,(0,0,255),2,cv2.LINE_AA)
                
                frame = cv2.cvtColor(main_frame, cv2.COLOR_BGR2RGB)
                self.return_image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)


class shapefinder(QThread):
    """
    Created on Mon Feb 18 12:31:45 2019
    @author: Michael Osinowo
    """
    signal = pyqtSignal(list)
    
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.running = True
        self.new_frame_available = False
    
    def get_new_frame(self, frame, ret):
        self.new_frame = frame
        self.new_ret = ret
        self.new_frame_available = True
    
    def stop(self):
        self.running = False
    
    #calculate angle
    def angle(self, pt1,pt2,pt0):
        dx1 = pt1[0][0] - pt0[0][0]
        dy1 = pt1[0][1] - pt0[0][1]
        dx2 = pt2[0][0] - pt0[0][0]
        dy2 = pt2[0][1] - pt0[0][1]
        return float((dx1*dx2 + dy1*dy2))/math.sqrt(float((dx1*dx1 + dy1*dy1))*(dx2*dx2 + dy2*dy2) + 1e-10)
    
    def run(self):
        #dictionary of all contours
        contours = {}
        #array of edges of polygon
        approx = []
        #scale of the text
        scale = 2
        
        while self.running:
            if self.new_frame_available:
                self.new_frame_available = False
                
                ret, frame = self.new_ret, self.new_frame
                if ret==True:
                    triangles = 0
                    squares = 0
                    lines = 0
                    circles = 0
                    
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #grayscale conversion
                    #canny = cv2.Canny(frame,80,240,3)
                    blur = cv2.GaussianBlur(gray, (5, 5), 0)
                    ret,thresh1 = cv2.threshold(gray,60,250,cv2.THRESH_BINARY)
                    canny2, contours = cv2.findContours(thresh1,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)#contours
                    
                    for cnt in canny2:
                        #approximate the contour with accuracy proportional to
                        #the contour perimeter
                        approx = cv2.approxPolyDP(cnt,cv2.arcLength(cnt,True)*0.02,True)
                        #Skip small or non-convex objects
                        if(abs(cv2.contourArea(cnt))<100 or not(cv2.isContourConvex(approx))):
                            continue
                        
                        if(len(approx) == 1): #Line
                            lines = lines + 1
                            x,y,w,h = cv2.boundingRect(cnt)
            #                cv2.drawContours(frame, [approx], -1, (0,255,0), 3)
            #                cv2.putText(frame,'Line',(x,y),cv2.FONT_HERSHEY_SIMPLEX,scale,(255,255,255),2,cv2.LINE_AA)
                        
                        if(len(approx) == 3): #  Triangle
                            triangles = triangles + 1
                            x,y,w,h = cv2.boundingRect(cnt)
            #                cv2.drawContours(frame, [approx], -1, (0,255,0), 3)
            #                cv2.putText(frame,'TRI',(x,y),cv2.FONT_HERSHEY_SIMPLEX,scale,(255,255,255),2,cv2.LINE_AA)    
            
                        elif(len(approx)>=4 and len(approx)<=6):
                            #nb vertices of a polygonal curve
                            vtc = len(approx)
                            #get cos of all corners
                            cos = []
                            for j in range(2,vtc+1):
                                cos.append(self.angle(approx[j%vtc],approx[j-2],approx[j-1]))
                            #sort ascending cos
                            cos.sort()
                            #get lowest and highest
                            mincos = cos[0]
                            maxcos = cos[-1]
            
                            #Use the degrees obtained above and the number of vertices
                            #to determine the shape of the contour
                            x,y,w,h = cv2.boundingRect(cnt)
                            if(vtc==4):
                                squares = squares + 1
#                                cv2.drawContours(frame, [approx], -1, (0,255,0), 3)
#                                ar = w/float(h)
#                                if (ar >= 0.95 and ar <= 1.05):
#                                    cv2.putText(frame,'Square',(x,y),cv2.FONT_HERSHEY_SIMPLEX,scale,(255,255,255),2,cv2.LINE_AA)
#                                else:
#                                    cv2.putText(frame,'Rectangle',(x,y),cv2.FONT_HERSHEY_SIMPLEX,scale,(255,255,255),2,cv2.LINE_AA)      
#                                    
#                            elif(vtc==5):
#                                cv2.drawContours(frame, [approx], -1, (0,255,0), 3)
#                                cv2.putText(frame,'PENTA',(x,y),cv2.FONT_HERSHEY_SIMPLEX,scale,(255,255,255),2,cv2.LINE_AA)
#                            elif(vtc==6):
#                               cv2.drawContours(frame, [approx], -1, (0,255,0), 3)
#                                cv2.putText(frame,'HEXA',(x,y),cv2.FONT_HERSHEY_SIMPLEX,scale,(255,255,255),2,cv2.LINE_AA)
                        else:
                            #detect and label circle
                            area = cv2.contourArea(cnt)
                            x,y,w,h = cv2.boundingRect(cnt)
                            radius = w/2
                            if(abs(1 - (float(w)/h))<=2 and abs(1-(area/(math.pi*radius*radius)))<=0.2):
                                circles += 1
            #                    cv2.drawContours(frame, [approx], -1, (0,255,0), 3)
            #                    cv2.putText(frame,'CIRC',(x,y),cv2.FONT_HERSHEY_SIMPLEX,scale,(255,255,255),2,cv2.LINE_AA)
            
                    #Display the resulting frame
#                    out.write(frame)
            #        print('Squares : ' + str(squares))
            #        print('Circles : ' + str(circles))
            #        print('Triangles : ' + str(triangles))
            #        print('Lines : ' + str(lines))
                    
                    cv2.rectangle(frame,(5,5),(55,55),(0,0,255),-1)
                    cv2.circle(frame,(30,92), 30, (0,0,255), -1)
                    
                    pts = np.array([[30,130],[5,170],[55,170]],np.int32)
                    pts = pts.reshape((-1,1,2))
                    cv2.fillPoly(frame,[pts],(0,0,255))
            
                    cv2.line(frame,(5,200),(55,200),(0,0,255),3)
                    
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(frame,str(squares),(72,45), font, 1,(0,0,255),2,cv2.LINE_AA)
                    cv2.putText(frame,str(circles),(72,105), font, 1,(0,0,255),2,cv2.LINE_AA)
                    cv2.putText(frame,str(triangles),(72,160), font, 1,(0,0,255),2,cv2.LINE_AA)
                    cv2.putText(frame,str(lines),(72,210), font, 1,(0,0,255),2,cv2.LINE_AA)
                
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.return_image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)