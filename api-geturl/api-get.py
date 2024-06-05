from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/post_url', methods=['POST'])
def post_url():
    data = request.get_json()  # Get JSON data from POST request
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    urls = data.get('urls')  # Extract 'urls' field from JSON data
    if not urls:
        return jsonify({'error': 'No URLs provided'}), 400

    # Process the URLs
    for url in urls:
        # You can perform any processing you need here, such as saving to a database
        print("Received URL:", url)

    return jsonify({'message': 'URLs received successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)
