import cv2 
import numpy as np
import pandas as pd
import pickle
class CellTracker(object):
    def ImgSegmentation():
        pass

    def CellTrack(self,path):
        tracker_types = ['TLD', 'MEDIANFLOW',  'MOSSE', 'CSRT']
        tracker_type = tracker_types[2]
        #(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')￼
        print(cv2.__version__)
        minor_ver=4.0
        if int(minor_ver) < 3:
            tracker = cv2.Tracker_create(tracker_type)
        else:
            if tracker_type == 'TLD':
                tracker = cv2.TrackerTLD_create()
            if tracker_type == 'MEDIANFLOW':
                tracker = cv2.TrackerMedianFlow_create()
            if tracker_type == 'GOTURN':
                tracker = cv2.TrackerGOTURN_create()
            if tracker_type == 'MOSSE':
                tracker = cv2.TrackerMOSSE_create()
            if tracker_type == "CSRT":
                tracker = cv2.TrackerCSRT_create()
    
        video = cv2.VideoCapture(path)
    
        # Exit if video not opened.
        if not video.isOpened():
            print("Could not open video")
            sys.exit()
    
        # Read first frame.
        ok, frame = video.read()
        if not ok:
            print('Cannot read video file')
            sys.exit()
        
        bbox = (287, 23, 86, 320)
        bbox = cv2.selectROI(frame, False)
    
        # We pass the x,v co ordinates here from a classifier
        ok = tracker.init(frame, bbox)
    
        while True:
            # Read a new frame
            ok, frame = video.read()
            if not ok:
                break
            
            timer = cv2.getTickCount()
            ok, bbox = tracker.update(frame)
    
            fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);
    
            if ok:
                # Tracking success
                p1 = (int(bbox[0]), int(bbox[1]))
                p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
            else :
                # Tracking failure
                cv2.putText(frame, "Tracking failure detected", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)

            cv2.putText(frame, tracker_type + " Tracker", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2);
            cv2.putText(frame, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2);
            cv2.imshow("Tracking", frame)
    
            k = cv2.waitKey(1) & 0xff
            if k == 27 : break
            pass

    # Function to convert Vid to Np array
    def TransformData(self,path):
        frames=[]
        vid=cv2.VideoCapture(path)

        status,frame=vid.read()
        while (vid.isOpened() and status):
                temp =np.array(frame,dtype=np.uint8)
                frames.append(temp)
                status,frame=vid.read()
            
        frames2=np.array(frames)
        pickle.dumps(frames2)
                
    def Farnback(self,path):
        cv = cv2()
        cap = cv.VideoCapture(path)
        ret, first_frame = cap.read()
        # Converts frame to grayscale because we only need the luminance channel for detecting edges - less computationally expensive
        first_frame=np.array(first_frame,dtype=np.uint8)
        prev_gray = cv.cvtColor(first_frame, cv.COLOR_BGR2GRAY)
        mask = np.zeros_like(first_frame)
        mask[..., 1] = 255

        while(cap.isOpened()):

            ret, frame = cap.read()
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            flow = cv.calcOpticalFlowFarneback(prev_gray, gray, None, 0.8,1000, 15, 3, 2, 1.6, 0)
            magnitude, angle = cv.cartToPolar(flow[..., 0], flow[..., 1])
            mask[..., 0] = angle * 180 / np.pi / 2
            mask[..., 2] = cv.normalize(magnitude, None, 0, 255, cv.NORM_MINMAX)
            rgb = cv.cvtColor(mask, cv.COLOR_HSV2BGR)
            cv.imshow("dense optical flow", rgb)

            if cv.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv.destroyAllWindows()

        
if __name__=="__main__":
    obj=CellTracker()
    #path to video C:/Users/alienware/Downloads/color_movie_3.mp4
    #path=input()
    path="C:/Users/alienware/Downloads/color_movie_3.mp4"
    #obj.Farnback(path)
    obj.CellTrack(path)
    #obj.TransformData(path)