from elasticsearch import Elasticsearch, helpers
import logging
from flask import Flask, request, jsonify
import logstash
import sys, os
# ========================MASIH TENTATIF DIPAKE ATAU NGGA========================
# PATHNYA AGAK GAK JELAS BUAT IMPORT
# sys.path.append('/path/to/application/app/folder')
# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder#comment8761102_4383597
relative_path = "settings.py"
absolute_path = os.path.abspath(relative_path)
path_components = absolute_path.split(os.path.sep)
path_components.pop()
path_components.pop()
full_path = os.path.join(*path_components, "searchIndexing", "searchIndexing")
full_path_with_drive = str(os.path.join(path_components[0], os.path.sep, full_path))
print("XXXXXXXXX",full_path_with_drive)
# 'C:\File Coding Cloud Project\Project\search-indexing\searchIndexing\searchIndexing'
sys.path.insert(1, str(full_path_with_drive))
import settings as settings

app = Flask(__name__)

# Function to parse a log line into a dictionary
def parse_log_line(line):
    log_entry = {}
    parts = line.strip().split(', ')
    try:
        for part in parts:
            key, value = part.split(': ', 1)
            log_entry[key.strip()] = value.strip()
    except ValueError as e:
        logging.error(f"Error parsing line: {line.strip()}. Error: {e}")
        return None
    return log_entry if log_entry else None

# Generator function to read log file line by line
def read_log_file(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            yield parse_log_line(line)

# Generator function to generate actions for bulk indexing
def generate_actions(log_file_path, index_name):
    for log_entry in read_log_file(log_file_path):
        yield {
            "_index": index_name,
            "_source": log_entry
        }

# Function to create Elasticsearch index if it does not exist
    
# Endpoint to receive logs and send to Elasticsearch
@app.route('/upload_logs', methods=['POST'])
def upload_logs():
    data = request.get_json()
    index_name = data.get('index_name')
    
    if not index_name :
        return jsonify({'error': 'index_name are required'}), 400
    # Fetch Scrapy project settings
    log_file_path = settings.get_log_file_path()
    print("XXXXX", settings.get_elasticsearch_settings())
    # Connect to Elasticsearch using settings from settings.py
    getES = settings.get_elasticsearch_settings()
    es = Elasticsearch(
        [{'host': getES['host'], 'port': getES['port'], 'scheme': getES['scheme']}],  # Use 'http' for localhost
        basic_auth=getES['http_auth'],
        verify_certs=getES['verify_certs']  # Skip certificate verification for testing
    )
    
    # Check Elasticsearch connection
    if not es.ping():
        return jsonify({'error': 'Elasticsearch connection failed'}), 500

    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

    # Create index if it does not exist
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)
        print(f"Created index: {index_name}")
        return jsonify({'message': 'Logs uploaded successfully'}), 200
    
    return jsonify({'error': f'Duplicate LOGS'}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5002)
