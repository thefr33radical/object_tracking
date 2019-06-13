
from flask import Flask, render_template
import os


root_path = "/home/user/workdir/thefr33radical/object_tracking/template"
app = Flask(__name__,template_folder=root_path,root_path=root_path)


@app.route("/")
def home():
    print(os.getcwd())
    return render_template("index.html")


@app.route("/salvador")
def salvador():
    return "Hello, Salvador"

if __name__ == "__main__":
    app.run(debug=True)
