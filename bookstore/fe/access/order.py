import requests
from urllib.parse import urljoin


class Order:
    def __init__(self, url_prefix):
        self.url_prefix = urljoin(url_prefix, "order/")

    def new_order_cancel_manually(self, user_id: str, order_id: str):
        json = {
            "user_id": user_id,
            "order_id": order_id
        }
        url = urljoin(self.url_prefix, "new_order_cancel_manually")
        r = requests.post(url, json=json)
        return r.status_code

    def new_order_cancel_auto(self, order_id: str):
        json = {
            "order_id": order_id
        }
        url = urljoin(self.url_prefix, "new_order_cancel_auto")
        r = requests.post(url, json=json)
        return r.status_code

    def query_order_history(self, user_id: str):
        json = {
            "user_id": user_id
        }
        url = urljoin(self.url_prefix, "query_order_history")
        r = requests.post(url, json=json)
        return r.status_code
