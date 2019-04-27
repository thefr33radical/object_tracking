import cv2
import time
 
if __name__ == '__main__' :
 
    # Start default camera
    video = cv2.VideoCapture(0);
    print(type(video))
     