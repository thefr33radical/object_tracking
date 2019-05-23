from flask import Flask
app = Flask(__name__)

@app.route("/virtualreality")
def home():
    return "Hello, World!"
@app.route("/")
def salvador():
    return "Hello, virtualreality"
if __name__ == "__main__":
    app.run(debug=True)