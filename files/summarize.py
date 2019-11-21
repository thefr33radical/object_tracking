import os
import glob
import pandas as pd
import numpy as np

path2="H:/workdir/object_tracking/files/data"
def summarize(path):
        summary={}
        summary["ID"]=[]
        summary["condition"]=[]
        summary["session"]=[]
        summary["video"]=[]
        summary["success"]=[]
        summary["bounces"]=[]
        summary["number"]=[]
       
        for filename in glob.glob(os.path.join(path+'/*op1.csv')):
            t=os.path.splitext(os.path.basename(filename))
            f=path+"/"+t[0]+".csv"
           
            df=pd.read_csv(f)
            bounce= sum(df["bounce"].values)
            c=0

            for i in df["error"].values:
                if i>0:
                    c+=1            
            try:
                temp=t[0].split("_")
                                 
                summary["ID"].append(temp[0])
                summary["condition"].append(temp[1])
                summary["session"].append(temp[2])
                summary["video"].append(temp[3])
                summary["number"].append(temp[4])
                summary["bounces"].append(bounce)
                summary["success"].append(c)
            except:
                summary={}
                summary["ID"]=[]
                summary["condition"]=[]
                summary["session"]=[]
                summary["video"]=[]
                summary["success"]=[]
                summary["bounces"]=[]
                summary["number"]=[]
                temp=""
                c=0
                bounce=0                
                temp2=t[0].split("_")
                print(temp2[0],t)
                summary["ID"].append(temp2[0])
                summary["condition"].append(temp2[1])
                summary["session"].append(0)
                summary["video"].append(0)
                summary["number"].append(0)
                summary["bounces"].append(bounce)
                summary["success"].append(c)
                print(summary)            

            df4= pd.DataFrame.from_dict(summary)
           
            df4.to_csv(path+"/summary_"+t[0]+"_.csv")

            summary={}
            summary["ID"]=[]
            summary["condition"]=[]
            summary["session"]=[]
            summary["video"]=[]
            summary["success"]=[]
            summary["bounces"]=[]
            summary["number"]=[]
            temp=""
            c=0
            bounce=0

summarize(path2)
