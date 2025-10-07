from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")  # lädt /templates/index.html


if __name__ == "__main__":
    app.run(debug=True)  # http://127.0.0.1:5000
