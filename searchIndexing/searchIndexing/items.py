# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SearchindexingItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field(serializer=str)
    name = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()
    set_url = scrapy.Field()
    content = scrapy.Field()
    html_tags = scrapy.Field()
    class_tags = scrapy.Field()





