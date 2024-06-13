import scrapy
from searchIndexing.items import SearchindexingItem
import pymongo
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from bs4 import BeautifulSoup  # Import BeautifulSoup
import re
from collections import Counter  # Import Counter for counting unique elements
from scrapy.selector import Selector
from datetime import datetime
import random
import string

def generate_unique_id():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')  # Current timestamp in a specific format
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=6))  # Random string of 6 characters
    unique_id = f"{timestamp}_{random_str}"
    return unique_id

class SearchspiderSpider(scrapy.Spider):
    name = "searchspider"
    # start_urls = ["https://market.bisnis.com/read/20240529/7/1769261/saham-bren-prajogo-pangestu-langsung-arb-10-akibat-ppk-full-call-auction"]
    custom_settings ={
            'FEEDS' :{
                'booksdata.json' : {'format':'json' , 'overwrite':True}
            },
        }
    

    def __init__(self, *args, **kwargs): 
      super(SearchspiderSpider, self).__init__(*args, **kwargs) 
      self.start_urls = [kwargs.get('start_url')] 
      self.allowed_domains = kwargs.get('allowed_domains', [])  # Default to empty list
      self.rules = (
            Rule(LinkExtractor(allow=self.allowed_domains), callback='parse', follow=True),
            )

    def parse(self, response):
        book_item = SearchindexingItem()
        book_item['webId']=generate_unique_id()

        res = response.body
        # encoded_body = res.decode('utf-8')
        book_item['name'] = response.url,
        title = response.css('title::text').get()
        book_item['title'] = title

        # COMPLETELY HTML FILE===================================
                 # Clean HTML text using BeautifulSoup
        soup = BeautifulSoup(res, 'html.parser')
        formatted_html = soup.prettify(formatter='html')  # Indent with HTML formatting

        book_item['body'] =formatted_html,

        # GET ALL CLEAN CONTENT WITHOUT HTML ELEMEN =============================

        # Option 1: Basic cleaning (remove all HTML tags and extra spaces)
        text = soup.get_text(separator=' ')  # Get text with spaces as separator
        clean_text = re.sub(r'\s+', ' ', text).strip()  # Replace multiple spaces with single space and strip whitespace
        book_item['content'] = clean_text  # Option 1 result
        # EXTRACT ALL LINKS IN CURRENT PAGES ===============================
        # extracted_links = []
        extracted_links = [link.url for link in LinkExtractor(allow=self.allowed_domains).extract_links(response)]
   
        book_item['set_url'] = extracted_links
        # get html tags -------------------------------
        # Extract and count unique tags (excluding text and self-closing tags)
        all_tags = set(sorted(tag.name for tag in soup.find_all() if tag.name not in ('script')))
        # Save unique tags to a list
        book_item['html_tags']  = list(all_tags)

        # css tags------------------------------------------------------------------
         # Extract and build element hierarchy
        extracted_data = []
        indent = 0  # Track indentation level

        def build_hierarchy(element):
            nonlocal indent  # Access and modify the indent variable
            tag_name = element.name
            if 'class' in element.attrs:  # Check for class attribute
                classes = element['class']
                class_str = ' '.join(classes)  # Combine classes into a string
            else:
                class_str = ''

            entry = ""
            entry += indent * '  ' + "<"
            entry += tag_name

            if class_str:
                entry += ' class="' + class_str + '">'

            extracted_data.append(entry)
            indent += 1  # Increase indentation for child elements

            for child in element.children:
                if not isinstance(child, str):  # Skip text nodes
                    build_hierarchy(child)

            indent -= 1  # Decrease indentation for closing tag

            # Add closing tag entry
            closing_entry = indent * '  '+'<' + tag_name + "/>"
            extracted_data.append(closing_entry)

        build_hierarchy(soup)  # Start building hierarchy from the root element
        # Add tuple (tag, class)
        book_item['class_tags'] =list(extracted_data)
        
        print('-----------------', self.allowed_domains)



        yield book_item
