# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sys, os

# PATHNYA AGAK GAK JELAS BUAT IMPORT
relative_path = "requirements.txt"
absolute_path = os.path.abspath(relative_path)
path_components = absolute_path.split(os.path.sep)

path_components.pop()
full_path = os.path.join(*path_components,"logger")
full_path_with_drive = str(os.path.join(path_components[0], os.path.sep, full_path))

sys.path.insert(1, str(full_path_with_drive))

print(full_path_with_drive)

import custom_logger as CustomLogger

log_folder = 'C:\\File Coding Cloud Project\\Project\\search-indexing\\logs'
logger = CustomLogger.CustomLogger(log_folder)

class SearchindexingPipeline:
    def process_item(self, item, spider):
        logger.debug_log(f"Processing item in Pipeline: {item}", 'pipelines.py')
        return item

from pymongo import MongoClient

class SaveToMongoDBPipeline:
  def __init__(self):
    # Connect to MongoDB
    self.client = MongoClient("mongodb://localhost:27017/")
    self.db = self.client["cc-webcrawl"]  # Replace "books" with your database name

  def process_item(self, item, spider):
    # Get collection (table equivalent)
    collection = self.db["webcrawl"]  # Replace "books" with your collection name
    exists = collection.find_one({"content": item["content"]})
    title_exists = collection.find_one({"title": item["title"]})

    if not title_exists:
            # self.db[spider.name].insert_one(dict(item))
            collection.insert_one(item)
            logger.debug_log("Article added to MongoDB", 'pipelines.py')
    # Insert data into collection
    # collection.insert_one(item)

    return item

  def close_spider(self,spider):
    # Close connection
    self.client.close()

import requests
import json
from scrapy.exceptions import DropItem

class SendURLToAPIPipeline:
    def __init__(self, api_url):
        self.api_url = api_url

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            api_url=crawler.settings.get('API_URL')
        )

    def process_item(self, item, spider):
        if 'set_url' not in item:
            raise DropItem("Missing 'set_url' field in item")

        set_urls = item['set_url']
        payload = {'webId': item['webId'], 'urls': set_urls}

        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            logger.info_log(f"URLs sent to API: {set_urls}", 'pipelines.py')
        except requests.RequestException as e:
            logger.error_log(f"Failed to send URLs to API: {e}", 'pipelines.py')

        return item