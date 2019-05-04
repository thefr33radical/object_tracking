# import the necessary packages
from collections import deque
import numpy as np
import argparse
import time
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

ap = argparse.ArgumentParser()
args = vars(ap.parse_args())

# Initialize kinect objects
kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Body | PyKinectV2.FrameSourceTypes_BodyIndex | PyKinectV2.FrameSourceTypes_Color |
                                         PyKinectV2.FrameSourceTypes_Depth | PyKinectV2.FrameSourceTypes_Infrared)
# Default: 1920, 1080 video height and width for kinect
color_width, color_height = kinect.color_frame_desc.Width, kinect.color_frame_desc.Height

start = 0.0
end = 0.0
frame_counter = 0
kinect.has_new_color_frame()
time.sleep(2.0)

greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
pts = deque(maxlen=64)
print("iniitalizing default")
start = time.time()
print("start time : ", start)
while True:
    if kinect.has_new_color_frame():
        

        color_frame = kinect.get_last_color_frame()
        color_img = color_frame.reshape(((color_height, color_width, 4))).astype(np.uint8)
        color_img_resize = cv2.resize(color_img, (0, 0), fx=0.25, fy=0.25)
        #cv2.imshow('color', color_img_resize)

        frame = color_img_resize
        if frame is None:
            break

        # resize the frame, blur it, and convert it to the HSV
        # color space
        frame = imutils.resize(frame, width=800)
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        cv2.imshow('color', hsv)
        # construct a mask for the color "green", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, greenLower, greenUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        frame_counter += 1
    else:
        print("Iniitalizing afer a break")
        start = time.time() 
        print(start)

    key = cv2.waitKey(1)
    # Press Escape key to Quit
    if key == 27:
        end = time.time()
        fps = float(frame_counter/(end-start))
        print("End,FPS:",end,fps)
        break
