from flask import Flask, request, jsonify
from flask_cors import CORS
import re

# Create the Flask app instance
app = Flask(__name__)
# Allow CORS for frontend access
CORS(app)

# Define route for GET requests
@app.route("/", methods=["GET"])
def avg_word_length():
    text = request.args.get("text", "")
    # Use regex to remove punctuation
    clean_text = re.sub(r'[^\w\s]', '', text)
    words = clean_text.split()
    total_letters = sum(len(word) for word in words)
    total_words = len(words)

    if total_words == 0:
        avg = 0
    else:
        avg = round(total_letters / total_words, 2)

    # Return just the number as a string in 'description' field
    return jsonify({
        "result": avg,
        "description": str(avg)
    })

# Start the server on all interfaces, port 80
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
