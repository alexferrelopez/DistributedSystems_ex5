from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def monitor():
    return render_template("monitor.html")

if __name__ == "__main__":
    app.run(debug=True)
