# import the necessary packages
from collections import deque
import argparse
import time
from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
import cv2
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import datetime
import imutils
import logging
import math
import os

path=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))+"\\"
print(path)
class Record(object):

    def compute(self,ID,exp,session):
        print(ID,exp,session)
        # logging.basicConfig(level=logging.ERROR,filename=path+'tracker.log', format= '%(name)s - %(levelname)s - %(message)s',filemode="w")

        ap = argparse.ArgumentParser()
        args = vars(ap.parse_args())

        # Initialize kinect objects
        kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Body | PyKinectV2.FrameSourceTypes_BodyIndex | PyKinectV2.FrameSourceTypes_Color |
                                                PyKinectV2.FrameSourceTypes_Depth | PyKinectV2.FrameSourceTypes_Infrared)
        # Default: 1920, 1080 video height and width for kinect
        color_width, color_height = kinect.color_frame_desc.Width, kinect.color_frame_desc.Height
        cv2.namedWindow('Frame')
        
        frame_counter = 0

        # Camera Warmup time
        time.sleep(2.0)
   
        font = cv2.FONT_HERSHEY_SIMPLEX
        position_text = (5, 30)
        fontScale = 1
        fontColor = (0, 0, 0)

        time_stamp=deque()        

        print("iniitalizing default")
        start =  int(round(time.time()))
        trial=1
        fourcc = cv2.VideoWriter_fourcc(*"X264")
        out = cv2.VideoWriter(path+'\\video_data\\'+str(ID)+"_"+str(exp)+"_"+str(session)+"_"+str(trial)+'.mp4',fourcc, 30,  ( color_width, color_height))
        
        print(color_height,color_width)        
            
        while True:
            if kinect.has_new_color_frame():
                time_stamp.appendleft(datetime.datetime.utcnow())

                # Get image from kinect
                color_frame = kinect.get_last_color_frame()
                
                # kinect image is 1D reshape to 4d with required height and width
                color_img = color_frame.reshape(
                    ((color_height, color_width, 4))).astype(np.uint8)
                
                # Resize the image if needed, 1 indicates 100%
                color_img_resize = cv2.resize(color_img, (0, 0), fx=0.5, fy=0.5)
                frame2=color_img
                frame = color_img_resize
                frame=color_img_resize

                frame_counter += 1    
                current_time =  int(round(time.time()))
                timeelapse=current_time-start
                
                if timeelapse==0:
                    timeelapse=1
                
                fps_present = float(frame_counter/timeelapse)
                #print("Frame rate    ",frame_counter,timeelapse,fps_present)

                # Parameters to Display on Screen
                cv2.putText(frame, 'FPS : '+str(int(fps_present)),     position_text,
                                font,     fontScale,    fontColor,    2)

                cv2.putText(frame, 'Status : Recording TR'+str(int(trial)),      (5, 50),
                                font,     .6,     fontColor,    2)                
                     
                #show the frame to screen
                cv2.imshow("Frame", frame)
                # Save Frame, img size should be equal to inp size
                out.write(frame2)            

                # Press Escape key to Quit
                key = cv2.waitKey(1) & 0xFF

                # Press p to pause recording
                if key==ord('p'):
                    print(ord('p'))
                    while 1:
                        cv2.putText(frame, 'Status : Recording Paused',      (5, 50),
                                font,     0.6,    fontColor,    2)
                        #cv2.imshow("Frame", frame)
                        key = cv2.waitKey(1)
                        if key==ord('p'):
                            start =  int(round(time.time()))
                            frame_counter=0
                            break

                # Press space to start new experiment
                if key == 32:
                    trial+=1
                    out = cv2.VideoWriter(path+'\\video_data\\'+str(ID)+"_"+str(exp)+"_"+str(session)+"_"+str(trial)+'.mp4',fourcc, 30,  ( color_width, color_height))
                    # self.exit_routine(name,time_stamp,frame_counter,ballx_pts,bally_pts,batx_pts,baty_pts,error,bounce)
                    continue
                # Press escape to quit
                if key == 27:
                   # self.exit_routine(name,time_stamp,frame_counter,ballx_pts,bally_pts,batx_pts,baty_pts,error,bounce)
                    return
            else:
                logging.error(
                    "Iniitalizing afer a break in Video. Restarting Start", start)
                start =  int(round(time.time()))
                frame_counter=0

                key = cv2.waitKey(1)
                # Press Escape key to Quit
                if key == 27:
                   return

if __name__=="__main__":
    obj=Record()
    obj.compute("demo","demo_age","demo_exp")
    
