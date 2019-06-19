
from flask import Flask, render_template,request
import os
import pandas as pd
from object_tracker1 import ObjectTracker


root_path = "C:/Users/ReGameVR/Envs/regamevr_virtualenv/object_tracking/template"

app = Flask(__name__,template_folder=root_path,root_path=root_path)
obj=ObjectTracker()

@app.route("/")
def home():
   return render_template("index.html")


@app.route("/",methods=["POST"])
def home_return():
    print("Site initialized")
    
    try:
        if  request.form['action'] == 'Start':
            name=request.form. get("name")
            age=request.form. get("age")
            exp=request.form. get("exp")
            print(name,age,exp)
            obj.compute()
            return render_template("stop.html")
        elif  request.form['action'] == 'Stop':
            obj.set_val=0
            return render_template("index.html")
        #text = request.form['Experiment Number']
    except Exception as e:
        print(e)
    return "123"


@app.route("/salvador")
def salvador():
    return "Hello, Salvador"

if __name__ == "__main__":    
    app.run(debug=True)
