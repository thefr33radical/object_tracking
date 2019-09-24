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
from imutils.video import VideoStream
from imutils.video import FPS
import pickle
import os
from collections import Counter


font = cv2.FONT_HERSHEY_SIMPLEX
position_text = (10, 30)
position_text2 = (5, 6)
bat_text2 = (5, 90)
error_text = (5, 120)
fontScale = 1
fontColor = (255,255,255)
lineType = 2

kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Body | PyKinectV2.FrameSourceTypes_BodyIndex | PyKinectV2.FrameSourceTypes_Color |
                                         PyKinectV2.FrameSourceTypes_Depth | PyKinectV2.FrameSourceTypes_Infrared)
color_width, color_height = kinect.color_frame_desc.Width, kinect.color_frame_desc.Height                                        
with open(os.path.join(os.getcwd(), "rf_classifier.pkl"), "rb") as f:
    rf = pickle.load(f)

with open(os.path.join(os.getcwd(), "svc_classifier.pkl"), "rb") as f:
    svm = pickle.load(f)    
with open(os.path.join(os.getcwd(), "knn_classifier.pkl"), "rb") as f:
    knn = pickle.load(f)    
    
with open(os.path.join(os.getcwd(), "lr_classifier.pkl"), "rb") as f:
    lr = pickle.load(f) 
while True:
    if kinect.has_new_color_frame():
        color_frame = kinect.get_last_color_frame()
        # kinect image is 1D reshape to 4d with required height and width
        color_img = color_frame.reshape(
            ((color_height, color_width, 4))).astype(np.uint8)
        gray = cv2.cvtColor(color_img, cv2.COLOR_BGR2GRAY)
        img=np.array(gray)
        img = cv2.bitwise_not(img)
        img=cv2.resize(gray,(28,28))
        print(img)
        res_svm=svm.predict(img.reshape(1,-1))[0]
        res_knn=knn.predict(img.reshape(1,-1))[0]
        res_lr=lr.predict(img.reshape(1,-1))[0]
        res_rf=rf.predict(img.reshape(1,-1))[0]
    
        res= np.array([res_svm,res_knn,res_lr,res_rf],dtype=int)
        print(res)
        res=Counter(res)
        res=res.most_common()[0][0]
        cv2.putText(gray, 'Number Predicted  SVM :'+str(res_svm),    (10, 30),           font,     fontScale,    fontColor,    lineType)
        cv2.putText(gray, 'Number Predicted LR :'+str(res_lr),     (10, 60),           font,     fontScale,    fontColor,    lineType)
        cv2.putText(gray, 'Number Predicted KNN :'+str(res_knn),     (10, 90),           font,     fontScale,    fontColor,    lineType)
        cv2.putText(gray, 'Number Predicted RF :'+str(res_rf),     (10, 120),           font,     fontScale,    fontColor,    lineType)
        cv2.putText(gray, 'Number Predicted :'+str(res),     (10, 150),           font,     fontScale,    fontColor,    lineType)
        cv2.imshow("frame", gray)
    
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
