# import the necessary packages
from collections import deque
import numpy as np
#import pandas as pd
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
import object_tracker1


def exit_routine(frame_counter, start):
    end = time.time()
    fps = float(frame_counter/(end-start))
    print("FPS:",fps)

class ObjectTracker(object):
    def __init__(self):
        self.set_val=1

    def compute(self):
            
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
        kinect.has_new_color_frame()
        time.sleep(2.0)

        font = cv2.FONT_HERSHEY_SIMPLEX
        position_text = (5, 30)
        position_text2 = (5, 60)
        fontScale = 1
        fontColor = (255, 255, 255)
        lineType = 2
        # Queue to store trace points 
        pts = deque(maxlen=32)
        time_q =deque(maxlen=2)
        dist_q = deque(maxlen=2)
        print("iniitalizing default")
        start = time.time()
        print("start time : ", start)

        fourcc = cv2.VideoWriter_fourcc(*"X264")
        out = cv2.VideoWriter('output.mp4',fourcc, 30, ( color_width, color_height))
            
        while True and self.set_val:
            if kinect.has_new_color_frame():

                # Get image from kinect
                color_frame = kinect.get_last_color_frame()
                # kinect image is 1D reshape to 4d with required height and width
                color_img = color_frame.reshape(
                    ((color_height, color_width, 4))).astype(np.uint8)
                # Resize the image if needed, 1 indicates 100%
                color_img_resize = cv2.resize(color_img, (0, 0), fx=1, fy=1)
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

                # Find all contours which have green in them
                cnts = cv2.findContours(
                    mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)

                center = None

                if len(cnts) > 0:
                        # find the largest contour in the mask, then use
                        # it to compute the minimum enclosing circle and

                    c = max(cnts, key=cv2.contourArea)
                    ((x, y), radius) = cv2.minEnclosingCircle(c)
                    M = cv2.moments(c)

                    # only proceed if the radius meets a minimum size
                    if radius > 10:
                        # draw the circle and centroid on the frame,
                        # then update the list of tracked points

                        #x1,y1,w,h =  cv2.boundingRect(c)
                        #cv2.rectangle(frame,(x1,y1),(x1+w,y1+h),(0,255,0),2)
                        try:
                            # centroid, centre of the circle
                            center = (int(M["m10"] / M["m00"]),
                                    int(M["m01"] / M["m00"]))
                            # Draw the outer circle on the ball
                            cv2.circle(frame, (int(x), int(y)),
                                    int(radius), circle_color, 1)
                            # Draw the point circle on centroid and fill it
                            cv2.circle(frame, center, 5, trace_color, -1)

                            pts.appendleft(center)
                                                
                            if len(time_q)>1 and len(dist_q) >1:
                                d = dist_q.pop()
                                t = time_q.pop()
                                pr = time.time()
                                #speed =  math.sqrt( (center[0]-d[0])**2 + (center[1]-d[1])**2 ) / abs(t - pr)
                                speed =  abs(center[1]-d[1]) / abs(t - pr)
                                time_q.appendleft(pr)
                                dist_q.appendleft(center)

                            else:
                                time_q.appendleft(time.time())
                                dist_q.appendleft(center)

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
                    logging.warning("No ball detected")            
                    speed = 0
                    
                current_time = time.time()
                fps_present = float(frame_counter/(current_time-start))
                cv2.putText(frame, 'FPS:'+str(fps_present),     position_text,
                                font,     fontScale,    fontColor,    lineType)
                
                cv2.putText(frame, 'Speed:'+str(speed),     position_text2,
                                font,     fontScale,    fontColor,    lineType)
                # show the frame to our screen
                
                #frame = imutils.resize(frame, width=320,height =240)
                cv2.imshow("Frame", frame)

                out.write(frame)

                # Press Escape key to Quit
                key = cv2.waitKey(1) & 0xFF
                if key == 27:
                    exit_routine(frame_counter, start)
                    break
            else:
                logging.error(
                    "Iniitalizing afer a break in Video. Restarting Start", start)
                start = time.time()

            key = cv2.waitKey(1)
            # Press Escape key to Quit
            if key == 27:
                exit_routine(frame_counter, start)
                break

obj=ObjectTracker()
obj.compute()