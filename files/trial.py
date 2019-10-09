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
import datetime
import imutils
import logging
import math
import os

path=os.path.dirname(os.path.abspath(__file__))+"\\"

class ObjectTracker(object):

    def __init__(self):
        self.set_val=1
        self.mouseX=0
        self.mouseY=0
        self.mouse2X=0
        self.mouse2Y=0

    def exit_routine(self,name,time_data,frame_counter,ballx_pts,bally_pts,batx_pts,baty_pts,error,bounce):
        end =  int(round(time.time()))
        #fps = float(frame_counter/(end-start))

        csv1={}
        csv2={}
        csv3={}
        try:
            print("1")
            # csv1 comprises of continious information
            #csv1["name"]=str(name)
           # csv1["timestamp"]=0
            #print(path)
            print(len(bally_pts),len(baty_pts))
            csv1["ballposx"]=ballx_pts
            csv1["ballposy"]=bally_pts
            csv1["racketposx"]=batx_pts
            csv1["racketposy"]=baty_pts

            data_csv1=pd.DataFrame(csv1)
            
            data_csv1.to_csv(path+str(name)+"1"+".csv")
        except:
            pass

        # csv2 comprises of success information
        try:

            csv2["name"]=str(name)
            csv2["timestamp"]=time_data[0]
            csv2["trial"]=0
            csv2["Bounce Count"]=bounce

            success=0
            for i in error:
                if i==0:
                    success+=1
            
            csv2["Success"]=success            

            data_csv2=pd.DataFrame(csv1)
            data_csv2.to_csv(path+str(name)+"2"+".csv")
        except:
            pass
        # csv3 comprises of error information
        try:

            csv3["name"]=str(name)
            csv3["timestamp"]=time_data
            csv3["trial"]=0
            csv3["Number of Bounces"]=bounce*(len(error))
            csv3["Error"]=error
            
            data_csv3=pd.DataFrame(csv3)
            data_csv3.to_csv(path+str(name)+"3"+".csv")
        except:
            pass
       
    def compute(self,name,age,exp):
        
        # logging.basicConfig(level=logging.ERROR,filename=path+'tracker.log', format= '%(name)s - %(levelname)s - %(message)s',filemode="w")

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
        ballx_pts=deque()
        bally_pts=deque()

        batx_pts=deque()
        baty_pts=deque()

        font = cv2.FONT_HERSHEY_SIMPLEX
        position_text = (5, 30)
        position_text2 = (5, 60)
        bat_text2 = (5, 90)
        error_text = (5, 120)
        fontScale = 1
        fontColor = (255, 255, 255)
        lineType = 2
        line_pos=None

        # Queue to store trace points 
        pts = deque()
        bat_pts = []
        time_q = []
        dist_q = []
        time_stamp= []
        
        speed_data=deque()
        time_data=deque()
        error=deque()
        setline=0

        time_q2 =deque(maxlen=2)
        dist_q2 = deque(maxlen=2)
        speed_data2=deque()
        time_data2=deque()

        x=0;y=0
        x2=0;y2=0
        xline=0;yline=0
        threshold=40
        bounce=0


        

        print("iniitalizing default")
        start =  int(round(time.time()))
        #print("start time : ", start)

        fourcc = cv2.VideoWriter_fourcc(*"avc1")
        out = cv2.VideoWriter(path+'\\newoutput_'+str(exp)+'.mp4',fourcc, 30, ( 1980, 1080))
            
        while True:
            if kinect.has_new_color_frame():
                time_stamp.append(datetime.datetime.utcnow())

                # Get image from kinect
                color_frame = kinect.get_last_color_frame()
                
                # kinect image is 1D reshape to 4d with required height and width
                color_img = color_frame.reshape(
                    ((color_height, color_width, 4))).astype(np.uint8)
                
                # Resize the image if needed, 1 indicates 100%
                #color_img_resize = cv2.resize(color_img, (0, 0), fx=1, fy=1)
                #frame = color_img_resize
                frame=color_img
                if frame is None:
                    continue

                # resize the frame,if needed # frame = imutils.resize(frame, width=800)

                # blur the image
                blurred = cv2.GaussianBlur(frame, (11, 11), 0)
                # convert it to the HSV
                hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
                # apply mask -> only green colrs will be highlighted
                mask = cv2.inRange(hsv, (40, 86, 90), (64, 200, 240))
                # apply mask -> only blue colours will be highlighted
                bat_mask=cv2.inRange(hsv, (101,100,38), (110,255,255))
                # apply mask -> only red colours will be highlighted
                line_mask=cv2.inRange(hsv,  (0, 100, 100), (179, 255, 255))

                # (ball) Find all contours which have green in them 
                cnts = cv2.findContours(
                    mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)

                # (bat) Find all contours which have blue in them 
                cnts_bat = cv2.findContours(
                    bat_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts_bat = imutils.grab_contours(cnts_bat)

                # (Line) Find all contours which have red in them
                if setline==0:
                    cnts_line = cv2.findContours(
                        line_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    cnts_line = imutils.grab_contours(cnts_line)                
                    #print("contour", cnts_line)
                    setline=1
                    #cv2.namedWindow('Frame2')
                    
                center = None
                center_bat = None
                
                # Set Contours of line
                if len(cnts_line) > 0 and setline :
                    # find the largest contour in the mask, then use
                    # it to compute the minimum enclosing circle and
                    line_pos = max(cnts_line, key=cv2.contourArea) 
                    ((xline, yline), radius) = cv2.minEnclosingCircle(line_pos) 
                   
                    xline=int(xline)
                    yline=int(yline)
                    cv2.line(frame, (0,yline ), (960, int(yline)), (105,255,0), 3)
                    cv2.imshow('Frame',frame)
                                      
                else:
                    print("RED LINE NOT DETECTED")
                    return

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

                        try:
                            # centroid, centre of the circle for ball
                            center = (int(M["m10"] / M["m00"]),
                                    int(M["m01"] / M["m00"]))                            

                            # Draw the outer circle on the ball
                            cv2.circle(frame, (int(x), int(y)),
                                    int(radius), circle_color, 1)                            
                            pts.appendleft(center)
                            # Draw the point circle on centroid and fill it
                            cv2.circle(frame, center, 5, trace_color, -1)                        
                            # Compute Error of Ball across the line
                            print("center",center)
                            
                            ballx_pts.appendleft(center[0])
                            bally_pts.appendleft(center[1])
                            x=center[0]
                            y=center[1]
                            
                            # Error Logic. Maximum Height
                            if len(bally_pts)>=2:                                
                                # Record the maximum position
                                if bally_pts[-2]>bally_pts[-1]:
                                    # Positive Error
                                        error.appendleft(y - yline)
                                        cv2.putText(frame, 'Error : '+str(error[-1]),     error_text,
                            font,     fontScale,    fontColor,    lineType)
                               
                            

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
                    x=0;y=0
                    #pts.append(0)
                    #ballx_pts.appendleft(0)
                    #bally_pts.appendleft(0)
                    
                               
                # CASE 2
                # Find the contours of bat
                if len(cnts_bat)>0 :
                        # find the largest contour in the mask, then use
                        # it to compute the minimum enclosing circle and
                    c2 = max(cnts_bat,key=cv2.contourArea)                    
                    ((x2, y2), radius2) = cv2.minEnclosingCircle(c2)                  
                    M2 = cv2.moments(c2)
                    
                    # only proceed if the radius meets a minimum size
                    if radius2 >0:
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
                            #bat_pts.append(center2)
                            try:

                                batx_pts.appendleft(center2[0])
                                baty_pts.appendleft(center2[1])
                                x2=center2[0]
                                y2=center2[1]
                            except:
                                pass

                            # Computing Bounce
                            if threshold > abs(y2-y) :
                                 bounce+=1        

                                                   
                        except Exception as e:
                            logging.exception("Moments values are 0 error ")       
                else:
                    logging.warning("No bat detected") 
                    print('bat not detected')           
                    speed2=0
                    x2=0;y2=0

                # Update Frame Number    
                frame_counter += 1    
                current_time =  int(round(time.time()))
                timeelapse=current_time-start
                if timeelapse==0:
                    timeelapse=1
                
                fps_present = float(frame_counter/timeelapse)
                #print("Frame rate    ",frame_counter,timeelapse,fps_present)

                # Parameters to Display on Screen
                cv2.putText(frame, 'FPS :'+str(fps_present),     position_text,
                                font,     fontScale,    fontColor,    lineType)
            
            
                cv2.putText(frame, 'Ball Position :'+str(int(x))+' '+str(int(y)),     position_text2,
                            font,     fontScale,    fontColor,    lineType)
            
                cv2.putText(frame, 'Bat Position :'+str(int(x2))+' '+str(int(y2)),     bat_text2,
                            font,     fontScale,    fontColor,    lineType)
            
                
            
                # Draw Error Line
                lineThickness = 3
                #print(line_pos[0])
                cv2.line(frame, (0, yline), (960, yline), (255,255,0), lineThickness)
                #print("mouse",self.mouseY,self.mouse2Y )
                #cv2.line(frame, (0, self.mouse2Y), (960, self.mouse2Y), (0,200,0), lineThickness)
                    
                # show the frame to screen
                cv2.imshow("Frame", frame)
                # Save Frame, img size should be equal to inp size
                out.write(frame)
            
                # Press Escape key to Quit
                key = cv2.waitKey(1) & 0xFF
                if key == 27:
                    self.exit_routine(name,time_stamp,frame_counter,ballx_pts,bally_pts,batx_pts,baty_pts,error,bounce)
                    break
            else:
                logging.error(
                    "Iniitalizing afer a break in Video. Restarting Start", start)
                start =  int(round(time.time()))
                frame_counter=0

            key = cv2.waitKey(1)
            # Press Escape key to Quit
            if key == 27:
                self.exit_routine(name,time_stamp,frame_counter,ballx_pts,bally_pts,batx_pts,baty_pts,error,bounce)
                break

if __name__=="__main__":
    obj=ObjectTracker()
    obj.compute("demo","demo_age","demo_exp")
    red = np.uint8([[[0,255,0 ]]])
    hsv_green = cv2.cvtColor(red,cv2.COLOR_BGR2HSV)
    print (hsv_green)
