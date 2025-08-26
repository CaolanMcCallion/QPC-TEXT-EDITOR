from flask import Flask, request, jsonify
from flask_cors import CORS
import string

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def count_punctuation():
    text = request.args.get("text", "")
    punctuations = list(string.punctuation)
    
    # Count how many characters in the text are in the punctuation list
    punctuation_count = sum(1 for char in text if char in punctuations)

    return jsonify({
        "result": punctuation_count,
        "description": f"{punctuation_count}"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
