from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
import numpy as np
import cv2
import time
from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils

kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Body | PyKinectV2.FrameSourceTypes_BodyIndex | PyKinectV2.FrameSourceTypes_Color |
                                         PyKinectV2.FrameSourceTypes_Depth | PyKinectV2.FrameSourceTypes_Infrared)

color_width, color_height = kinect.color_frame_desc.Width, kinect.color_frame_desc.Height #  Default: 1920, 1080
start = 0.0
end =0.0
frame_counter =0
while True:
    # --- Getting frames and drawing
    if kinect.has_new_color_frame(): 
                                 
        color_frame      = kinect.get_last_color_frame() 
        color_img        = color_frame.reshape(((color_height, color_width, 4))).astype(np.uint8)
        color_img_resize = cv2.resize(color_img, (0,0), fx=0.5, fy=0.5)
        print(type(color_frame),type(color_img))
        cv2.imshow('color', color_img)
        #out = cv2.VideoWriter('output.avi', -1, 30.0, (640,480))  
        frame_counter += 1
        key=cv2.waitKey(1)
        # Press Escape key to Quit
        if key == 27:
            end = time.time()
            fps = float(frame_counter/(end-start))
            print(fps)
            break
     
    else:
        start = time.time() 


    key = cv2.waitKey(1)
    # Press Escape key to Quit
    if key == 27:
        print("end2")
        break
