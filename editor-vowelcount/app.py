from flask import Flask, request, jsonify
from flask_cors import CORS

# Create Flask app instance
app = Flask(__name__)
# Enables CORS to allow frontend requests from other origins
CORS(app)



# Define the main GET endpoint for counting vowels
@app.route("/", methods=["GET"])
def count_vowels():
    # Get the 'text' query param from the request
    text = request.args.get("text", "")
    # Count the number of vowels in the input string
    count = sum(1 for c in text.lower() if c in "aeiou")
    # Returns the result in JSON 
    return jsonify({
        "result": count,
        "description": f"{count} vowels found"
    })
# Run the Flask app on port 80, which is accessible from any host
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
