from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
conn = sqlite3.connect('db.sqlite', check_same_thread=False)

cursor = conn.cursor()
# Create the table if it doesn't exist
cursor.execute("CREATE TABLE IF NOT EXISTS urls_tes (id INTEGER PRIMARY KEY AUTOINCREMENT,urls VARCHAR(255) NOT NULL,pageid VARCHAR(255) NULL,created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);")
@app.route('/', methods=["GET"])
def posts():
    # sql = """INSERT INTO urls_tes (urls) VALUES ("tes")"""
    # cursor.execute(sql)
    cursor.execute('''
      SELECT * FROM urls_tes
    ''')
   
    data = cursor.fetchall()

    return jsonify(data)

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
