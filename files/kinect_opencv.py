from pykinect2 import PyKinectV2
#import utils_PyKinectV2 as utils
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
import numpy as np
import cv2
#import utils

kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Body | 
                                         PyKinectV2.FrameSourceTypes_BodyIndex |
                                         PyKinectV2.FrameSourceTypes_Color |
                                         PyKinectV2.FrameSourceTypes_Depth |
                                         PyKinectV2.FrameSourceTypes_Infrared)

depth_width, depth_height = kinect.depth_frame_desc.Width, kinect.depth_frame_desc.Height # Default: 512, 424
color_width, color_height = kinect.color_frame_desc.Width, kinect.color_frame_desc.Height # Def
while True:
    # --- Getting frames and drawing
    if  kinect.has_new_color_frame():                           
        color_frame      = kinect.get_last_color_frame() 
        color_img        = color_frame.reshape(((color_height, color_width, 4))).astype(np.uint8)
        color_img_resize = cv2.resize(color_img, (0,0), fx=0.5, fy=0.5)   
        cv2.imshow('color', color_img)        
        #align_color_img  = utils.get_align_color_image(kinect, color_img) # Add this to get the color image that is aligned to depth frame size
        # res = cv2.bitwise_and(color_img_resize,color_img_resize,mask = body_index_img) # Replace this line with the below
        #res = cv2.bitwise_and(align_color_img,align_color_img,mask = body_index_img)
        
    else:
        print("no")

    key = cv2.waitKey(1)
    if key == 27: break



"""from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
import numpy as np
import cv2

kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color)

while True:
    # --- Getting frames and drawing
    if   kinect.has_new_color_frame():

              body_frame       = kinect.get_last_color_frame()
              body_index_frame = kinect.get_last_body_index_frame()                               
              color_frame      = kinect.get_last_color_frame()

              body_index_img   = body_index_frame.reshape(((depth_height, depth_width))).astype(np.uint8)
              #body_index_img  =  cv2.resize(body_index_img,(960, 540),None, fx=0.5, fy=0.5)
              color_img        = color_frame.reshape(((color_height, color_width, 4))).astype(np.uint8)
              color_img_resize = cv2.resize(color_img, None, fx=0.5, fy=0.5) # Resize (1080, 1920, 4) into half (540, 960, 4)
              #body_index_img  =  utils.color_body_index(kinect, body_index_img) # Add color to body_index_img
                                
                                
              body_index_img= cv2.bitwise_not(body_index_img)
              cv2.imshow('Bi',body_index_img)
                               
              res = cv2.bitwise_and(color_img_resize,color_img_resize,mask = body_index_img)
              cv2.imshow('Res',res)

    key = cv2.waitKey(1)
    if key == 27: break

        """
"""
https://stackoverflow.com/questions/53905324/pykinect2-extract-depth-data-from-individule-pixel-kinectv2
https://github.com/Kinect/PyKinect2/issues/67
from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
import numpy as np
import cv2

kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Depth)

while True:
    # --- Getting frames and drawing
    if kinect.has_new_depth_frame():
        frame = kinect.get_last_depth_frame()
        frameD = kinect._depth_frame_data
        frame = frame.astype(np.uint8)
        frame = np.reshape(frame, (424, 512))
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        def click_event(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                print(x, y)
            if event == cv2.EVENT_RBUTTONDOWN:
                Pixel_Depth = frameD[((y * 512) + x)]
                print(Pixel_Depth)
        ##output = cv2.bilateralFilter(output, 1, 150, 75)
        cv2.imshow('KINECT Video Stream', frame)
        cv2.setMouseCallback('KINECT Video Stream', click_event)
        output = None

    key = cv2.waitKey(1)
    if key == 27: break
        """