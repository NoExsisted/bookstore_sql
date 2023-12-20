import requests
from urllib.parse import urljoin


class Send_Receive:
    def __init__(self, url_prefix):
        self.url_prefix = urljoin(url_prefix, "send_receive/")

    def send_books(self, seller_id: str, order_id: str):
        json = {"user_id": seller_id, "order_id": order_id}
        # print(simplejson.dumps(json))
        url = urljoin(self.url_prefix, "send_books")
        r = requests.post(url, json=json)
        return r.status_code

    def receive_books(self, user_id: str, order_id: str):
        json = {"user_id": user_id, "order_id": order_id}
        # print(simplejson.dumps(json))
        url = urljoin(self.url_prefix, "receive_books")
        r = requests.post(url, json=json)
        return r.status_code
