# import the necessary packages
from collections import deque
import numpy as np
import pandas as pd
import argparse
import time
from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
import numpy as np
import cv2
from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import logging
import math

class ObjectTracker(object):
    def __init__(self):
        self.set_val=1
        self.mouseX=0
        self.mouseY=0
        self.mouse2X=0
        self.mouse2Y=0

    def exit_routine(self,frame_counter, start,name,age,exp,speed_data,time_data,speed_data2,time_data2,ballposx,ballposy,racketx,rackety):
        end =  int(round(time.time()))
        #fps = float(frame_counter/(end-start))
        info={}
        cont={}

        cont["timestamp"]=time_data
        cont["name"]=str(name)
        cont["ballposx"]=ballposx
        cont["ballposy"]=ballposy
        cont["racketposx"]=str(racketx)*len(time_data)
        cont["racketposy"]=str(rackety)*len(time_data)

        op=pd.DataFrame(cont)
        op.to_csv("H:\workdir\object_tracking\output_cont"+str(exp)+".csv")

        info["name"]=str(name)
        info["age"]=age
        info["exp"]=exp
        #info["fps"]=fps
        info["ball_speed"]=speed_data

        z=[]

        for i in range(len(time_data)):
          z.append(np.random.choice(["success","fail"]))
        info["#success"]=z

            
        info["#bounces"]=np.random.randint(0,3,len(time_data))
        #info["bat_speed"]=speed_data2

        #print("length",len(speed_data),len(speed_data2))
        #info["error"]=[]
        
        #info["ball_time"]=time_data
        #info["bat_time"]=time_data2
        output=pd.DataFrame(info)
        #print("FPS:",fps)
        output.to_csv("H:\workdir\object_tracking\output_"+str(exp)+".csv")

        # Function to get input from mouse
    def draw_circle(self,event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDBLCLK:
            self.mouseX,self.mouseY = x,y            
          
        if event == cv2.EVENT_RBUTTONDBLCLK:
            self.mouse2X,self.mouse2Y = x,y
       
    def compute(self,name,age,exp):
        path = "c:/Users/ReGameVR/Envs/regamevr_virtualenv/object_tracking/"
        #logging.basicConfig(level=logging.ERROR,filename=path+'tracker.log', format= '%(name)s - %(levelname)s - %(message)s',filemode="w")

        ap = argparse.ArgumentParser()
        args = vars(ap.parse_args())

        # Initialize kinect objects
        kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Body | PyKinectV2.FrameSourceTypes_BodyIndex | PyKinectV2.FrameSourceTypes_Color |
                                                PyKinectV2.FrameSourceTypes_Depth | PyKinectV2.FrameSourceTypes_Infrared)
        # Default: 1920, 1080 video height and width for kinect
        color_width, color_height = kinect.color_frame_desc.Width, kinect.color_frame_desc.Height
        cv2.namedWindow('Frame')
        
        print("Frame_width, Frame_height", color_width, color_height)
        
        circle_color = (0, 255, 255)
        trace_color = (0, 0, 255)
        start = 0.0
        end = 0.0
        frame_counter = 0
        speed =0
        speed2=0
        kinect.has_new_color_frame()
        # Camera Warmup time
        time.sleep(2.0)

        font = cv2.FONT_HERSHEY_SIMPLEX
        position_text = (5, 30)
        position_text2 = (5, 60)
        bat_text2 = (5, 90)
        error_text = (5, 120)
        fontScale = 1
        fontColor = (255, 255, 255)
        lineType = 2
        # Queue to store trace points 
        pts = deque(maxlen=32)
        bat_pts = deque(maxlen=32)
        time_q =deque(maxlen=2)
        dist_q = deque(maxlen=2)
        speed_data=deque()
        time_data=deque()
        error=deque()
        setline=1

        time_q2 =deque(maxlen=2)
        dist_q2 = deque(maxlen=2)
        speed_data2=deque()
        time_data2=deque()

        print("iniitalizing default")
        start =  int(round(time.time()))
        #print("start time : ", start)

        fourcc = cv2.VideoWriter_fourcc(*"avc1")
        out = cv2.VideoWriter('output_'+str(exp)+'.mp4',fourcc, 30, ( 960, 540))
            
        while True:
            if kinect.has_new_color_frame():

                # Get image from kinect
                color_frame = kinect.get_last_color_frame()
                # kinect image is 1D reshape to 4d with required height and width
                color_img = color_frame.reshape(
                    ((color_height, color_width, 4))).astype(np.uint8)
                # Resize the image if needed, 1 indicates 100%
                color_img_resize = cv2.resize(color_img, (0, 0), fx=0.5, fy=0.5)
                frame = color_img_resize

                if frame is None:
                    break

                # resize the frame,if needed # frame = imutils.resize(frame, width=800)
                # blur the image
                blurred = cv2.GaussianBlur(frame, (11, 11), 0)
                # convert it to the HSV
                hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
                # apply mash -> only green colrs will be highlighted
                mask = cv2.inRange(hsv, (40, 86, 90), (64, 200, 240))
                bat_mask=cv2.inRange(hsv, (101,100,38), (110,255,255))
                line_mask=cv2.inRange(hsv, (0,160,0), (20,255,255))

                # (ball) Find all contours which have green in them 
                cnts = cv2.findContours(
                    mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)

                # (bat) Find all contours which have blue in them 
                cnts_bat = cv2.findContours(
                    bat_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts_bat = imutils.grab_contours(cnts_bat)

                cnts_line = cv2.findContours(
                    line_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts_line = imutils.grab_contours(cnts_line)
                
                #print("contour", cnts_line)

                center = None
                center_bat = None
                
                # Capture Mouse Clicks to form Error Line
                #cv2.setMouseCallback("Frame",self.draw_circle)
                if len(cnts_line) > 0 and setline :
                    # find the largest contour in the mask, then use
                    # it to compute the minimum enclosing circle and
                    c3 = max(cnts_line, key=cv2.contourArea)                    
                    ((self.mouseX, self.mouseY), radius) = cv2.minEnclosingCircle(c3) 
                    self.mouseX=int(self.mouseX)     
                    self.mouseY=int(self.mouseY)              
                    self.mouse2X=self.mouseX
                    self.mouse2Y=self.mouseY+200
                    setline=0
                    
                # CASE 1

                # Find the contours of ball
                if len(cnts) > 0 :
                        # find the largest contour in the mask, then use
                        # it to compute the minimum enclosing circle and
                    c = max(cnts, key=cv2.contourArea)                    
                    ((x, y), radius) = cv2.minEnclosingCircle(c)                    
                    M = cv2.moments(c)
                    
                    # only proceed if the radius meets a minimum size
                    if radius > 0:
                        print("got ball radius")
                        # draw the circle and centroid on the frame,
                        # then update the list of tracked points

                        #x1,y1,w,h =  cv2.boundingRect(c)
                        #cv2.rectangle(frame,(x1,y1),(x1+w,y1+h),(0,255,0),2)
                        try:
                            # centroid, centre of the circle for ball
                            center = (int(M["m10"] / M["m00"]),
                                    int(M["m01"] / M["m00"]))                            

                            # Draw the outer circle on the ball
                            cv2.circle(frame, (int(x), int(y)),
                                    int(radius), circle_color, 1)                            

                            # Draw the point circle on centroid and fill it
                            cv2.circle(frame, center, 5, trace_color, -1)
                            pts.appendleft(center)                            

                            # Compute Error of Ball across the line
                            if center[1] >self.mouseY and center[1] < self.mouse2Y:
                                error.appendleft(0)
                            if center[1] < self.mouseY:
                                error.appendleft(self.mouseY-center[1])
                            else:
                                error.appendleft(self.mouse2Y-center[1])

                            # Compute Speed, Distance if previous data exists in Queue else insert First data into Queue
                            if len(time_q)>1 and len(dist_q) >1 :
                                d = dist_q.pop()
                                t = time_q.pop()
                                pr = time.time()
                                #speed =  math.sqrt( (center[0]-d[0])**2 + (center[1]-d[1])**2 ) / abs(t - pr)
                                speed =  abs(center[1]-d[1]) / abs(t - pr)
                                # Converting on the basis of 1px=3.1cms
                                speed = speed * 3.1
                                time_q.appendleft(pr)
                                dist_q.appendleft(center)
                                speed_data.appendleft(speed)
                                time_data.appendleft(pr)                          
                            else:
                                speed_data.appendleft(0)
                                time_data.appendleft(0)
                                time_q.appendleft(time.time())
                                dist_q.appendleft(center)

                            # Compute Trail of the Ball
                            for i in range(1, len(pts)):
                                if pts[i - 1] is None or pts[i] is None:
                                    continue
                                try:
                                    thickness = int(np.sqrt(64 / float(i + 1)) * 1.5)
                                    cv2.line(frame, pts[i - 1], pts[i],
                                            (0, 120, 255), thickness)
                                except Exception as e:
                                    logging.exception(
                                        "Computing error in line thickness ")
                        except Exception as e:
                            logging.exception("Moments values are 0 error ")       
                else:
                    logging.warning("No ball detected") 
                    print('ball not detected')           
                    speed=0  
           
                # CASE 2

                # Find the contours of bat
                if len(cnts_bat)>0 :
                        # find the largest contour in the mask, then use
                        # it to compute the minimum enclosing circle and
                    c2 = max(cnts_bat,key=cv2.contourArea)                    
                    ((x2, y2), radius2) = cv2.minEnclosingCircle(c2)                  
                    M2 = cv2.moments(c2)
                    
                    # only proceed if the radius meets a minimum size
                    if radius2 >10:
                        print("got bat radius")
                        # draw the circle and centroid on the frame, for bat detected
                        #                      
                        try:
                            # centroid, centre of the circle for bat
                            center2 = (int(M2["m10"] / M2["m00"]),
                                    int(M2["m01"] / M2["m00"]))                           

                            # Draw the outer circle on the bat
                            cv2.circle(frame, (int(x2), int(y2)),
                                    int(radius2), circle_color, 1)                       

                            # Draw the point circle on centroid and fill it
                            cv2.circle(frame, center2, 5, trace_color, -1)
                            bat_pts.appendleft(center2)                  

                            # Compute Speed, Distance if previous data exists in Queue else insert First data into Queue
                            if  len(time_q2)>1 and len(dist_q2) >1 :
                                d2 = dist_q2.pop()
                                t2 = time_q2.pop()
                                pr2 = time.time()
                                #speed =  math.sqrt( (center[0]-d[0])**2 + (center[1]-d[1])**2 ) / abs(t - pr)
                                speed2 =  abs(center2[1]-d2[1]) / abs(t2 - pr2)
                                time_q2.appendleft(pr2)
                                dist2_q.appendleft(center2)
                                speed_data2.appendleft(speed2)
                                time_data2.appendleft(pr2)
                            else:
                                speed_data2.appendleft(0)
                                time_data2.appendleft(0)
                                time_q2.appendleft(time.time())
                                dist_q2.appendleft(center2)                            
                        except Exception as e:
                            logging.exception("Moments values are 0 error ")       
                else:
                    logging.warning("No bat detected") 
                    print('bat not detected')           
                    speed2=0

                # Update Frame Number    
                frame_counter += 1    
                current_time =  int(round(time.time()))
                timeelapse=current_time-start
                if timeelapse==0:
                    timeelapse=1
                
                
                fps_present = float(frame_counter/timeelapse)
                print("Frame rate    ",frame_counter,timeelapse,fps_present)

                # Parameters to Display on Screen
                cv2.putText(frame, 'FPS :'+str(fps_present),     position_text,
                                font,     fontScale,    fontColor,    lineType)
                
                cv2.putText(frame, 'Ball Speed :'+str(speed),     position_text2,
                                font,     fontScale,    fontColor,    lineType)
              
                cv2.putText(frame, 'Bat Speed :'+str(speed2),     bat_text2,
                                font,     fontScale,    fontColor,    lineType)
                try:

                    cv2.putText(frame, 'Error : '+str(error[0]),     error_text,
                                font,     fontScale,    fontColor,    lineType)
                except :
                    print("No Error")
                # Draw Error Line
                lineThickness = 3
                cv2.line(frame, (0, self.mouseY), (960, self.mouseY), (0,255,0), lineThickness)
                #print("mouse",self.mouseY,self.mouse2Y )
                cv2.line(frame, (0, self.mouse2Y), (960, self.mouse2Y), (0,200,0), lineThickness)
                
                # show the frame to screen
                cv2.imshow("Frame", frame)
                # Save Frame, img size should be equal to inp size
                out.write(frame)

                # Press Escape key to Quit
                key = cv2.waitKey(1) & 0xFF
                if key == 27:
                    self.exit_routine(frame_counter, start,name,age,exp,speed_data,time_data,speed_data2,time_data2,x,y,x2,y2)
                    break
            else:
                logging.error(
                    "Iniitalizing afer a break in Video. Restarting Start", start)
                start =  int(round(time.time()))
                frame_counter=0

            key = cv2.waitKey(1)
            # Press Escape key to Quit
            if key == 27:
                self.exit_routine(frame_counter, start,name,age,exp,speed_data,time_data,speed_data2,time_data2,x,y,x2,y2)
                break

if __name__=="__main__":
    obj=ObjectTracker()
    obj.compute("demo","demo_age","demo_exp")
    red = np.uint8([[[0,255,0 ]]])
    hsv_green = cv2.cvtColor(red,cv2.COLOR_BGR2HSV)
    print (hsv_green)