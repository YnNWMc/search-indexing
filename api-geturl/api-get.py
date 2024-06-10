from flask import Flask, request, jsonify
import sqlite3
import requests
import re

app = Flask(__name__)
conn = sqlite3.connect('db.sqlite', check_same_thread=False)

def is_valid_url(url):
    # Regular expression for validating a URL
    regex = re.compile(
        r'^(https?:\/\/)?'  # http:// or https://
        r'(([A-Za-z0-9-]+\.)+[A-Za-z]{2,})'  # domain
        r'(\/\S*)?$'  # path
    )
    return re.match(regex, url) is not None

def check_url_status(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)  # HEAD request for efficiency
        if response.status_code < 400:
            return True
    except requests.RequestException as e:
        print(f"Error checking URL {url}: {e}")
    return False


cursor = conn.cursor()
# Create the table if it doesn't exist
cursor.execute("CREATE TABLE IF NOT EXISTS urls (id INTEGER PRIMARY KEY AUTOINCREMENT,url VARCHAR(255) NOT NULL,status VARCHAR(255) NOT NULL,web_id VARCHAR(255) NULL,created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);")
@app.route('/', methods=["GET"])
def posts():
    cursor.execute('''
      SELECT * FROM urls
    ''')
   
    data = cursor.fetchall()

    return jsonify(data)

@app.route('/api/post_url', methods=['POST'])
def post_url():
    data = request.get_json()  # Get JSON data from POST request
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400
    webId = data.get('webId')  # Extract 'urls' field from JSON data

    urls = data.get('urls')  # Extract 'urls' field from JSON data
    if not urls:
        return jsonify({'error': 'No URLs provided'}), 400
    try:
        new_urls = []
        for url in urls:
            status = "valid"
            if not is_valid_url(url):
                print(f"Invalid URL format: {url}")
                status = "not valid"  # Skip invalid URL format

            if not check_url_status(url):
                print(f"URL is not accessible or returns an error: {url}")
                status = "not valid"    # Skip URL that is not accessible
            # Check if URL already exists in the database
            cursor.execute("SELECT 1 FROM urls WHERE url = ?", (url,))
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute("INSERT INTO urls (url,status,web_id) VALUES (?,?,?)", (url,status,webId))
                new_urls.append(url)
        
        # Commit all new inserts at once
        conn.commit()

        if new_urls:
            print('New URLs inserted successfully ')
            return jsonify({'message': 'New URLs inserted successfully', 'urls': new_urls}), 200
        else:
            print('No new URLs to insert; all URLs already exist ')
            return jsonify({'message': 'No new URLs to insert; all URLs already exist'}), 200
    except Exception as e:
        # Rollback in case of any error
        conn.rollback()
        print('error: ' + str(e))
        return jsonify({'error': str(e)}), 500

    # return jsonify({'message': 'URLs received successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)
