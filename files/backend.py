import cv2 
import numpy as np
import pickle
import os
import requests
import pandas as pd
from collections import Counter
import time
import imutils
import datetime
import glob
import sys

save_path="H:/workdir/object_tracking/files/data/"
path="H:/workdir/object_tracking/files/bounce videos"

class ObjTrack(object):
    def __init__(self):
        self.data={}
        self.data["ballx"]=[]
        self.data["bally"]=[]
        self.data["batx"]=[]
        self.data["baty"]=[]
        self.data["timestamp"]=[]
        self.data["name"]=[]
      
        self.lvl={}
        self.lvl["error"]=[]
        self.lvl["bounce#"]=[]
        self.lvl["trial#"]=[]
        self.lvl["experiment_condition"]=[]
        self.lvl["timestamp"]=[]
        self.lvl["name"]=[]

        self.lvl2={}
        self.lvl2["success"]=[]
        self.lvl2["bounce"]=[]
        self.lvl2["trial#"]=[]
        self.lvl2["experiment_condition"]=[]
        self.lvl2["timestamp"]=[]
        self.lvl2["name"]=[]

    def detect_line(self,frame):
        # Only red color will be high lighted
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)   
        lower = np.array([0,50,20])
        upper = np.array([5,255,255])    
        mask = cv2.inRange(hsv,lower, upper)
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        if len(cnts) > 0:
                # find the largest contour in the mask, then use
                # it to compute the minimum enclosing circle and
            c = max(cnts, key=cv2.contourArea)
            ((lx, ly), radius) = cv2.minEnclosingCircle(c)
            print(" line  points",lx,ly)
            return int(lx),int(ly),mask
        return None,None,None

    def detect_ball(self,frame):

        # apply mash -> only green colors will be highlighted
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)       
        mask = cv2.inRange(hsv, (50, 60, 60), (70, 255,255))
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        #print(len(cnts))
        if len(cnts) > 0:
                # find the largest contour in the mask, then use
                # it to compute the minimum enclosing circle and
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            radius=int(radius)
            #print("radius",int(radius))
            if  radius > 2:
                return int(x),int(y),mask
        return None,None,None

    def detect_bat(self,frame):
    
        # apply mash -> only blue colrs will be highlighted
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        mask = cv2.inRange(hsv, (100,50,50), (110,255,255))
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        if len(cnts) > 0:
                # find the largest contour in the mask, then use
                # it to compute the minimum enclosing circle and
            c = max(cnts, key=cv2.contourArea)
            ((lx, ly), radius) = cv2.minEnclosingCircle(c)
            return int(lx),int(ly),mask
        return None,None,None

    def save_data(self,y,line_y,l,threshold=None):
        df=pd.DataFrame.from_dict(self.data)
        df2=pd.DataFrame.from_dict(self.lvl)
        df3=pd.DataFrame.from_dict(self.lvl2)
        threshold=7
        #df.resample('name', how='mean', fill_method='pad')
        try:

            b_list=[]
            e_list=[]
            b=0
            e=0
            z=[0]*threshold
            b_list+=z
            e_list+=z

            for i in range(threshold,len(df)-threshold):
                low =df.loc[i-threshold:i-1,"bally"].values
                high=df.loc[i+1:i+threshold,"bally"].values
                
                if all(df.loc[i,"bally"] > j for j in low) and all(df.loc[i,"bally"] > k for k in high):
                    print(" ---- great Success ---- ")
                    b=1
                    e= df.loc[i-1,"bally"]-line_y
                else:
                    b=0
                    e=0
                b_list.append(b)
                e_list.append(e)
            
            
            if len(b_list)< len(df):
                for j in range(len(b_list),len(df)):
                    b_list.append(0)
                    e_list.append(0)
            print("-------------------",len(b_list),len(df))
            df["bounce"]=b_list
            df["error"]=e_list

           
            df3.to_csv(save_path+l[0]+"_"+l[1]+"_"+l[2]+"_"+l[3]+"_"+l[4]+"_op3.csv")
            df2.to_csv(save_path+l[0]+"_"+l[1]+"_"+l[2]+"_"+l[3]+"_"+l[4]+"_op2.csv")    
            df.to_csv(save_path+l[0]+"_"+l[1]+"_"+l[2]+"_"+l[3]+"_"+l[4]+"_op1.csv")
            return
        except:
            b_list=[]
            e_list=[]
            b=0
            e=0
            z=[0]*threshold
            b_list+=z
            e_list+=z

            for i in range(threshold,len(df)-threshold):
                low =df.loc[i-threshold:i-1,"bally"].values
                high=df.loc[i+1:i+threshold,"bally"].values
                
                if all(df.loc[i,"bally"] > j for j in low) and all(df.loc[i,"bally"] > k for k in high):
                    print(" ---- great Success ---- ")
                    b=1
                    e= df.loc[i-1,"bally"]-line_y
                else:
                    b=0
                    e=0
                b_list.append(b)
                e_list.append(e)
            
            if len(b_list)< len(df):
                for j in range(len(b_list),len(df)):
                    b_list.apend(0)
                    e_list.append(0)
                      
            df["bounce"]=b_list
            df["error"]=e_list

            print("-------------------",len(b_list),len(df))
            df3.to_csv(save_path+"default_op3.csv")
            df2.to_csv(save_path+"default_op2.csv")
            df.to_csv(save_path+"default_op1.csv")

    def compute(self,path):
        filename=os.path.splitext(os.path.basename(path))[0]
        l=filename.split("_")

        font = cv2.FONT_HERSHEY_SIMPLEX
        position_text = (5, 30)
        position_text2 = (5, 60)
        fontScale = 1
        fontColor = (255, 255, 255)
        lineType = 2

        line_set=0
        line_x=0
        line_y=0
        line_mask=None

        x=0
        y=0
        bat_x=0
        bat_y=0
        bat_mask=None

        threshold_dist=280

        bounce=0
        success=0

        cap= cv2.VideoCapture(path)
        fcount=0   
        while(cap.isOpened()):
            
            ret, frame = cap.read() 
            try:
                color_img_resize = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
                frame = color_img_resize
            except:
                fcount+=1
                
                if fcount >2:
                    print("-------BAD VIDEO------",fcount)
                    self.save_data(y,line_y,l)
                    return
                    
                continue
                if cv2.waitKey(1) & 0xFF == ord('q'):   
                    self.save_data(y,line_y,l)
                    return                          
                
            if line_set==0:
                line_x,line_y,line_mask=self.detect_line(frame)
                #print("]]]]]]]]]]]]]]]]] line y",line_x,line_y,line_mask)
                line_set=1
                
                if line_x is None or line_y is None or line_mask is None:
                    cv2.putText(frame,"LINE POS NOT DETECTED!!!",    (10, 30), font,     fontScale,    fontColor,    lineType)
                    cv2.imshow("Frame", frame)
                    return

            # get co-ordinates of ball
            x,y,ball_mask=self.detect_ball(frame)
            if x is None or y is None or ball_mask is None:
                x=0
                y=0
                #frame3=ball_mask
                cv2.putText(frame,"Ball POS "+str(x)+" "+str(y),    (10, 120), font,     fontScale,    fontColor,    lineType)
                cv2.imshow("Frame", frame)        
                continue
                
            # get co-ordinates of bat
            bat_x,bat_y,bat_mask=self.detect_bat(frame)
            if bat_x is None or bat_y is None or bat_mask is None:
                #cv2.putText(frame,"Bat POS NOT DETECTED!!!",    (10, 30), font,     fontScale,    fontColor,    lineType)
                #cv2.imshow("Frame", frame)
                bounce=0
                continue
            
            a=np.array((bat_x,y))
            b=np.array((bat_x,bat_y))
            dist = np.linalg.norm(a-b)

            delay =1
            if dist < 120 and bat_y < y:
                #print("dist",dist)
                bounce+=1

                if y > line_y:
                    #print("success",y,line_y)
                    success=1
                else:
                    success=0
                
                self.lvl2["success"].append(success)
                self.lvl2["bounce"].append(bounce)
                self.lvl2["trial#"].append(bat_x)
                try:
                    self.lvl2["experiment_condition"].append(l[1])
                except:
                    self.lvl2["experiment_condition"].append("error_expcondition")
                self.lvl2["timestamp"].append(time.time())
                self.lvl2["name"].append(l[0])

                self.lvl["error"].append(dist)
                self.lvl["bounce#"].append(bounce)
                self.lvl["trial#"].append(bat_x)
                try:
                    self.lvl["experiment_condition"].append(l[1])
                except:
                    self.lvl["experiment_condition"].append("error_expcondition")
                self.lvl["timestamp"].append(time.time())
                self.lvl["name"].append(l[0])
            
            self.data["ballx"].append(x)
            self.data["bally"].append(y)
            self.data["batx"].append(bat_x)
            self.data["baty"].append(bat_y)
            self.data["timestamp"].append(time.time())
            self.data["name"].append(l[0])

            cv2.putText(frame,"Ball POS "+str(x)+" "+str(y),    (10, 30), font,     fontScale,    fontColor,    lineType)
            cv2.putText(frame,"Bat POS "+str(bat_x)+" "+str(bat_y),    (10, 60), font,     fontScale,    fontColor,    lineType)
            cv2.putText(frame,"Bounce "+str(dist),    (10, 90), font,     fontScale,    fontColor,    lineType)
            #cv2.putText(frame,"Bounce "+str(dist),    (10, 90), font,     fontScale,    fontColor,    lineType)
            cv2.imshow("Frame", frame)

            #frame2=cv2.bitwise_or(line_mask,ball_mask)
            #frame2=cv2.bitwise_or(frame2,line_mask)
            cv2.imshow("Frame2", line_mask) 
            #cv2.imshow("Frame3", frame2) 
           
            # limit Frame rate
            now = time.time()
            frameLimit = 50.0
            timeDiff = time.time() - now
            if (timeDiff < 1.0/(frameLimit)): 
                time.sleep( 1.0/(frameLimit) - timeDiff )

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.save_data(y,line_y,l)
                
                cap.release()
                cv2.destroyAllWindows()
                return

        self.save_data(y,line_y,l)
        cap.release()
        cv2.destroyAllWindows()
        return

if __name__=="__main__":
    #path=sys.argv[0]
    for f in glob.glob(os.path.join(path+'/*.mp4')):
        obj= ObjTrack()    
        print(os.path.basename(f))
        obj.compute(path+"/"+os.path.basename(f))
