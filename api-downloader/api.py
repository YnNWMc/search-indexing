from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import logging
# from scrapy.crawler import crawler

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins on all routes

# Global variables
scraping_in_progress = False
headers = {'Access-Control-Allow-Origin': "*",
        'Access-Control-Allow-Methods': "*",
        'Access-Control-Allow-Headers': "*"}

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set logging level as needed

# Endpoint to initiate scraping
@app.route('/scrape', methods=['POST'])
def scrape():
    global scraping_in_progress
    data = request.json  # Receive JSON data from frontend
    
    if not data or 'url' not in data:
        return jsonify({'error': 'Invalid request'}), 400
    
    if scraping_in_progress:
        return jsonify({'message': 'Scraping already in progress. Please wait.'}), 400

    target_url = data['url']
    allowed_domains = data.get('allowed_domains', [])
    scraping_in_progress = True


    # Launch Scrapy spider in background using subprocess
    command = [
        'scrapy',
        'crawl',
        'searchspider',
        '-a', f'start_url={target_url}',
        '-a', f'allowed_domains={",".join(allowed_domains)}'
    ]

    logging.info(f"Launching spider with command: {' '.join(command)}")
    subprocess.Popen(command, cwd='..\searchIndexing\searchIndexing')

    return jsonify({'message': 'Scraping initiated. Please wait for results.'}), 200

# Masih Error
# @app.route('/stop-scraping', methods=['GET'])
# def stop_scraping():
#     global scraping_in_progress

#     if not scraping_in_progress:
#         return jsonify({'message': 'No scraping in progress.'}), 400

#     # Attempt to stop the spider using Scrapy's crawler object
#     try:
#         crawler._signal_shutdown(9, 0)  # Send SIGKILL (9) signal with exit code 0
#     except Exception as e:
#         return jsonify({'error': f'Error stopping scraping: {str(e)}'}), 500

#     scraping_in_progress = False
#     return jsonify({'message': 'Scraping stopped successfully.'}), 200

if __name__ == '__main__':
    app.run(debug=True)
