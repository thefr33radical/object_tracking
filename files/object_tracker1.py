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

    def exit_routine(self,frame_counter, start,name,age,exp,speed_data,time_data,speed_data2,time_data2):
        end = time.time()
        fps = float(frame_counter/(end-start))
        info={}
        info["name"]=name
        info["age"]=age
        info["exp"]=exp
        info["fps"]=fps
        info["ball_speed"]=speed_data
        #info["bat_speed"]=speed_data2

        print("length",len(speed_data),len(speed_data2))
        #info["error"]=[]
        
        info["ball_time"]=time_data
        #info["bat_time"]=time_data2
        output=pd.DataFrame(info)
        print("FPS:",fps)
        output.to_csv("output_"+str(exp)+".csv")

    def compute(self,name,age,exp):
            
        path = "c:/Users/ReGameVR/Envs/regamevr_virtualenv/object_tracking/"
        logging.basicConfig(level=logging.ERROR,filename=path+'tracker.log', format= '%(name)s - %(levelname)s - %(message)s',filemode="w")

        ap = argparse.ArgumentParser()
        args = vars(ap.parse_args())

        # Initialize kinect objects
        kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Body | PyKinectV2.FrameSourceTypes_BodyIndex | PyKinectV2.FrameSourceTypes_Color |
                                                PyKinectV2.FrameSourceTypes_Depth | PyKinectV2.FrameSourceTypes_Infrared)
        # Default: 1920, 1080 video height and width for kinect
        color_width, color_height = kinect.color_frame_desc.Width, kinect.color_frame_desc.Height
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

        time_q2 =deque(maxlen=2)
        dist_q2 = deque(maxlen=2)
        speed_data2=deque()
        time_data2=deque()

        print("iniitalizing default")
        start = time.time()
        print("start time : ", start)

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

                # (ball) Find all contours which have green in them 
                cnts = cv2.findContours(
                    mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)

                # (bat) Find all contours which have blue in them 
                cnts_bat = cv2.findContours(
                    bat_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts_bat = imutils.grab_contours(cnts_bat)

                print("bat contour", cnts_bat)

                center = None
                center_bat = None

                # case 1
                # Find the contours of the bat and ball
                if len(cnts) > 0 and len(cnts_bat)>0:
                        # find the largest contour in the mask, then use
                        # it to compute the minimum enclosing circle and

                    c = max(cnts, key=cv2.contourArea)
                    c2 = max(cnts_bat,key=cv2.contourArea)
                    
                    ((x, y), radius) = cv2.minEnclosingCircle(c)
                    ((x2, y2), radius2) = cv2.minEnclosingCircle(c2)

                    M = cv2.moments(c)
                    M2 = cv2.moments(c2)

                    # only proceed if the radius meets a minimum size
                    if radius > 10 and radius2 >10:
                        print("got both radius")
                        # draw the circle and centroid on the frame,
                        # then update the list of tracked points

                        #x1,y1,w,h =  cv2.boundingRect(c)
                        #cv2.rectangle(frame,(x1,y1),(x1+w,y1+h),(0,255,0),2)
                        try:
                            # centroid, centre of the circle for ball
                            center = (int(M["m10"] / M["m00"]),
                                    int(M["m01"] / M["m00"]))
                            # centroid, centre of the circle for bat
                            center2 = (int(M2["m10"] / M2["m00"]),
                                    int(M2["m01"] / M2["m00"]))

                            # Draw the outer circle on the ball
                            cv2.circle(frame, (int(x), int(y)),
                                    int(radius), circle_color, 1)
                            # Draw the outer circle on the bat
                            cv2.circle(frame, (int(x2), int(y2)),
                                    int(radius2), circle_color, 1)

                            # Draw the point circle on centroid and fill it
                            cv2.circle(frame, center, 5, trace_color, -1)
                            cv2.circle(frame, center2, 5, trace_color, -1)

                            pts.appendleft(center)
                            bat_pts.appendleft(center2)

                            if center[1] >150 and center[1] < 400:
                                error.appendleft(0)
                            if center[1] < 150:
                                error.appendleft(150-center[1])
                            else:
                                error.appendleft(400-center[1])

                            if len(time_q)>1 and len(dist_q) >1 and len(time_q2)>1 and len(dist_q) >1:
                                d = dist_q.pop()
                                t = time_q.pop()
                                pr = time.time()
                                #speed =  math.sqrt( (center[0]-d[0])**2 + (center[1]-d[1])**2 ) / abs(t - pr)
                                speed =  abs(center[1]-d[1]) / abs(t - pr)
                                time_q.appendleft(pr)
                                dist_q.appendleft(center)

                                speed_data.appendleft(speed)
                                time_data.appendleft(pr)

                                # Bat speed
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
                                speed_data.appendleft(0)
                                time_data.appendleft(0)
                                time_q.appendleft(time.time())
                                dist_q.appendleft(center)

                                speed_data2.appendleft(0)
                                time_data2.appendleft(0)
                                time_q2.appendleft(time.time())
                                dist_q2.appendleft(center2)

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
                
                    # Update Frame Number
                    frame_counter += 1
                
                
                else:
                    logging.warning("No ball and bat detected") 
                    print('ball, bat not detected')           
                    speed=0
                    speed2=0
                    
                current_time = time.time()
                fps_present = float(frame_counter/(current_time-start))
                cv2.putText(frame, 'FPS:'+str(fps_present),     position_text,
                                font,     fontScale,    fontColor,    lineType)
                
                cv2.putText(frame, 'Ball Speed:'+str(speed),     position_text2,
                                font,     fontScale,    fontColor,    lineType)
              
                cv2.putText(frame, 'Bat Speed:'+str(speed2),     bat_text2,
                                font,     fontScale,    fontColor,    lineType)
                cv2.putText(frame, 'Error:'+str(error),     error_text,
                                font,     fontScale,    fontColor,    lineType)

                lineThickness = 2
                cv2.line(frame, (0, 150), (960, 150), (0,255,0), lineThickness)
                cv2.line(frame, (0, 400), (960, 400), (0,255,0), lineThickness)
                # show the frame to our screen
                
                #frame = imutils.resize(frame, width=320,height =240)
                cv2.imshow("Frame", frame)
                out.write(frame)

                # Press Escape key to Quit
                key = cv2.waitKey(1) & 0xFF
                if key == 27:
                    self.exit_routine(frame_counter, start,name,age,exp,speed_data,time_data,speed_data2,time_data2)
                    break
            else:
                logging.error(
                    "Iniitalizing afer a break in Video. Restarting Start", start)
                start = time.time()

            key = cv2.waitKey(1)
            # Press Escape key to Quit
            if key == 27:
                self.exit_routine(frame_counter, start,name,age,exp,speed_data,time_data,speed_data2,time_data2)
                break

if __name__=="__main__":
    obj=ObjectTracker()
    obj.compute("demo","demo_age","demo_exp")