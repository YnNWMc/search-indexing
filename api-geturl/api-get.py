from flask import Flask, request, jsonify
import sqlite3
import requests
from flask_cors import CORS
import re
from datetime import datetime, timedelta
import sys, os

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins on all routes

# PATHNYA AGAK GAK JELAS BUAT IMPORT
relative_path = "custom_logger.py"
absolute_path = os.path.abspath(relative_path)
path_components = absolute_path.split(os.path.sep)
path_components.pop()
path_components.pop()
full_path = os.path.join(*path_components, "logger")
full_path_with_drive = str(os.path.join(path_components[0], os.path.sep, full_path))

sys.path.insert(1, str(full_path_with_drive))

# sys.path.insert(1, "C:\File Coding Cloud Project\Project\search-indexing\logger")
import custom_logger as CustomLogger

log_folder = 'C:\\File Coding Cloud Project\\Project\\search-indexing\\logs'
logger = CustomLogger.CustomLogger(log_folder)


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
        logger.error_log(f"Error checking URL {url}: {e}","api-get.py")

    return False


cursor = conn.cursor()
# Create the table if it doesn't exist
cursor.execute("CREATE TABLE IF NOT EXISTS urls (id INTEGER PRIMARY KEY AUTOINCREMENT,url VARCHAR(255) NOT NULL,status VARCHAR(255) NOT NULL,web_id VARCHAR(255) NULL,created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);")
@app.route('/', methods=["GET"])
def posts():
    try:
        cursor.execute("SELECT * FROM urls")
        data = cursor.fetchall()
        logger.info_log("Fetched all URLs","api-get.py")
        return jsonify(data), 200
    except Exception as e:
        logger.error_log(f"Error fetching URLs: {e}","api-get.py")
        return jsonify({'error': str(e)}), 500

@app.route('/api/post_url', methods=['POST'])
def post_url():
    data = request.get_json()  # Get JSON data from POST request
    if not data:
        logger.error_log("No JSON data received in request","api-get.py")
        return jsonify({'error': 'No JSON data received'}), 400
    webId = data.get('webId')  # Extract 'urls' field from JSON data

    urls = data.get('urls')  # Extract 'urls' field from JSON data
    if not urls:
        logger.error_log("No URLs provided in request","api-get.py")
        return jsonify({'error': 'No URLs provided'}), 400
    try:
        new_urls = []
        for url in urls:
            status = "valid"
            if not is_valid_url(url):
                logger.warning_log(f"Invalid URL format: {url}","api-get.py")
                status = "not valid"  # Skip invalid URL format

            if not check_url_status(url):
                logger.warning_log(f"URL is not accessible or returns an error: {url}","api-get.py")
                status = "not valid"    # Skip URL that is not accessible
            # Check if URL already exists in the database
            cursor.execute("SELECT 1 FROM urls WHERE url = ?", (url,))
            exists = cursor.fetchone()
            
            # if status valid send url to downloader
            
            if not exists:
                cursor.execute("INSERT INTO urls (url,status,web_id) VALUES (?,?,?)", (url,status,webId))
                new_urls.append(url)
        
        # Commit all new inserts at once
        conn.commit()

        if new_urls:
            logger.info_log(f"New URLs inserted successfully: {new_urls}","api-get.py")
            return jsonify({'message': 'New URLs inserted successfully', 'urls': new_urls}), 200
        else:
            logger.info_log("No new URLs to insert; all URLs already exist","api-get.py")
            return jsonify({'message': 'No new URLs to insert; all URLs already exist'}), 200
    except Exception as e:
        # Rollback in case of any error
        conn.rollback()
        logger.error_log(f"Error inserting URLs: {e}","api-get.py")
        return jsonify({'error': str(e)}), 500
    
# Buat update datatable -- Sudah bisa secara real time
@app.route('/fetch-data', methods=["GET"])
def fetch_data():
    # Parameters sent by DataTables
    draw = int(request.args.get('draw', 0))
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))  # Default length if not provided
    search_value = request.args.get('search[value]', '')
    order_column = request.args.get('order[0][column]', 0)
    order_direction = request.args.get('order[0][dir]', 'asc')

    # Map DataTables column index to database column
    columns = ['id', 'url', 'status', 'web_id', 'created_at']
    sort_column = columns[int(order_column)]

    try:
        # Base query to retrieve URLs from the database
        query = "SELECT id, url, status, web_id, created_at FROM urls"

        # Apply search filter if provided
        if search_value:
            query += f" WHERE url LIKE '%{search_value}%'"

        # Apply ordering
        query += f" ORDER BY {sort_column} {order_direction}"

        # Apply pagination
        query += f" LIMIT {length} OFFSET {start}"

        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()

        # Total records before filtering
        total_records = cursor.execute("SELECT COUNT(*) FROM urls").fetchone()[0]

        # Structure the data to return as JSON
        urls = [
            {
                'id': row[0],
                'url': row[1],
                'status': row[2],
                'web_id': row[3],
                'created_at': row[4]
            }
            for row in data
        ]

        # Return response dlm json, karena datatable terimanya dalam json
        response = {
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': total_records,  
            'data': urls
        }
        logger.info_log("Fetched data for DataTables","api-get.py")
        
        return jsonify(response), 200

    except Exception as e:
        logger.error_log(f"Error fetching recently created data: {e}","api-get.py")
        return jsonify({'error': str(e)}), 500
    
    
@app.route('/fetch-recently-scraped', methods=["GET"])
def fetch_recently_created():
    # Parameters sent by DataTables
    draw = int(request.args.get('draw', 0))
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))  # Default length if not provided
    search_value = request.args.get('search[value]', '')
    order_column = request.args.get('order[0][column]', 0)
    order_direction = request.args.get('order[0][dir]', 'asc')

    # Map DataTables column index to database column
    columns = ['id', 'url', 'status', 'web_id', 'created_at']
    sort_column = columns[int(order_column)]

    try:
        # Base query to retrieve recently created URLs from the database
        query = "SELECT id, url, status, web_id, created_at FROM urls"
        query += " WHERE created_at >= ?"  # Fetch URLs created after this timestamp

        # Apply search filter if provided
        if search_value:
            query += f" AND url LIKE '%{search_value}%'"

        # Apply ordering
        query += f" ORDER BY {sort_column} {order_direction}"

        # Apply pagination
        query += f" LIMIT {length} OFFSET {start}"

        cursor = conn.cursor()
        
        # Fetch URLs created after a certain timestamp (adjust the timestamp as needed)
        created_after_timestamp = datetime.utcnow() - timedelta(minutes=5)  # Example: Created within the last 15 minutes
        cursor.execute(query, (created_after_timestamp,))
        data = cursor.fetchall()

        # Total records before filtering
        total_records = cursor.execute("SELECT COUNT(*) FROM urls WHERE created_at >= ?", (created_after_timestamp,)).fetchone()[0]

        # Structure the data to return as JSON
        urls = [
            {
                'id': row[0],
                'url': row[1],
                'status': row[2],
                'web_id': row[3],
                'created_at': row[4]
            }
            for row in data
        ]

        response = {
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': total_records,  # For simplicity, we assume no additional filtering on the server side
            'data': urls
        }
        logger.info_log("Fetched recently created data for DataTables","api-get.py")
        return jsonify(response), 200

    except Exception as e:
        logger.error_log(f"Error fetching recently created data: {e}","api-get.py")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
