
from flask import Flask, render_template,request
import os
import pandas as pd
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from object_tracker1 import ObjectTracker

# Set root path
# set static path
template_path =os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"\\template"
print("ROOT PATH",template_path)

app = Flask(__name__,template_folder=template_path)
app.static_folder=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"\\template\\static"
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
            obj.compute(name,age,exp)
            return render_template("stop.html")
        elif  request.form['action'] == 'Stop':
            obj.set_val=0
            return render_template("index.html")
        #text = request.form['Experiment Number']
    except Exception as e:
        print(e)
    return render_template("stop.html")


@app.route("/test")
def test():
    return "Hello, test complete"

if __name__ == "__main__":    
    app.run(debug=True)
