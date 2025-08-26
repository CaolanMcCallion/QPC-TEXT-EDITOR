from flask import Flask, request, jsonify  # Imports Flask and JSON tools
from flask_cors import CORS  # Imports CORS to allow frontend requests

app = Flask(__name__)  # Creates the Flask app instance
CORS(app)  # Enable CORS for all domains

# Defines the route for the microservice
@app.route("/", methods=["GET"])
def longest_word():
    text = request.args.get("text", "")  # Gets the input text from the query string
    words = text.split()  # Splits the input into a list of words

    # If there are no words then it sets result to an empty string
    if not words:
        result = ""
    else:
        result = max(words, key=len)  # Finds the longest word using max()

    # Returns just the longest word
    return jsonify({
        "result": result
    })

# Runs the app on port 80 (inside the container)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)

# Added this line to test git commits
