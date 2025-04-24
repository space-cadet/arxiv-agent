from flask import Flask

app = Flask(__name__)

@app.route("/")  # Route for the homepage
def home():
    return "Hello, Flask!"

if __name__ == "__main__":
    app.run(debug=True)  # Starts the dev server
