import requests
from urllib.parse import urljoin


class Search:
    def __init__(self, url_prefix):
        self.url_prefix = urljoin(url_prefix, "search/")

    def search_books(self, store_id, search_query, search_scopes):
        json = {
            "store_id": store_id,
            "search_query": search_query,
            "search_scopes": search_scopes
        }
        url = urljoin(self.url_prefix, "search_books")
        r = requests.post(url, json=json)
        return r.status_code, r.json()
