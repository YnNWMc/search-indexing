from flask import Flask, request, jsonify
import subprocess  # For launching Scrapy spider in background

app = Flask(__name__)

@app.route('/scrape', methods=['GET'])
def scrape():
    # Validate URL format (optional)
    # ...
    target_url = request.args.get('url')
    allowed_domains = request.args.getlist('allowed_domains')  # Returns a list

    # Launch Scrapy spider in background using subprocess
    command = [ 
            'scrapy',
            'crawl',
            'searchspider',
            '-a', f'start_url={target_url}',  # Pass URL as argument
            '-a', f'allowed_domains={",".join(allowed_domains)}'  # Join domains as a comma-separated string
        ]
    subprocess.Popen(command, cwd='./searchIndexing/searchIndexing')

    # Return a success message or placeholder response while scraping happens
    return jsonify({'message': 'Scraping initiated. Please wait for results.'})

if __name__ == '__main__':
    app.run(debug=True)