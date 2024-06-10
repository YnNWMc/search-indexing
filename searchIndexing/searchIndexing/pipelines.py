# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import logging


class SearchindexingPipeline:
    def process_item(self, item, spider):
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
            logging.debug("Article added to MongoDB")
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
        payload = {'webId':item['webId'],'urls': set_urls}

        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            spider.logger.info(f"URLs sent to API: {set_urls}")
        except requests.RequestException as e:
            spider.logger.error(f"Failed to send URLs to API: {e}")

        return item