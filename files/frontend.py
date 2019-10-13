
from flask import Flask, render_template,request
import os
import pandas as pd
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from trail import Record
import signal 
import multiprocessing
path = os.path.dirname(os.path.abspath(__file__))
#exp cond : control, restricted, enhanced
# seesion baseline, post aquistion
# Set root path
# set static path
template_path =os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"\\template"
print("ROOT PATH",template_path)

app = Flask(__name__,template_folder=template_path)
app.static_folder=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"\\template\\static"
obj=Record()

@app.route("/")
def home():
   return render_template("index.html")


@app.route("/",methods=["POST"])
def home_return():
    print("Site initialized")
    child_pid=None
    p1=None
    try:
        if  request.form['action'] == 'Start':
            name=request.form.get("name")
            exp=request.form.get("exp")
            session=request.form.get("session")
            print(name,exp,session) 
            p1 = multiprocessing.Process(target=obj.compute(name,exp,session)) 
            p1.start()
            child_pid=p1.pid
            with open (path+"\\data.txt","w+") as f:
                f.write(str(child_pid))
            print(child_pid)
            p1.join()
            #p1.close()
            print(p1)
            return render_template("stop.html")
        elif  request.form['action'] == 'Stop':
            file=None
            try:                
                return render_template("index.html")
            except:                        
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
