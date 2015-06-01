import requests
import os

response =requests.get("https://www.goodreads.com/book/review_counts.json?format=json&isbns=0486284735&key="+ os.environ['GR_KEY'])
