import pytest

from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.send_receive import Send_Receive
from fe.access.book import Book
from fe import conf
import uuid


class TestSendReceive:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_receive_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_receive_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_receive_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        gen_book = GenBook(self.seller_id, self.store_id)
        self.seller = gen_book.seller  # 卖家

        ok, self.buy_book_id_list = gen_book.gen(
            non_exist_book_id=False,
            low_stock_level=False,
            max_book_count=5
        )
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok

        b = register_new_buyer(self.buyer_id, self.password)  # 注册买家
        self.buyer = b
        code, self.order_id = b.new_order(self.store_id, self.buy_book_id_list)
        assert code == 200

        self.total_price = 0
        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            if book.price is None:
                continue
            else:
                self.total_price = self.total_price + book.price * num

        code = self.buyer.add_funds(self.total_price)
        assert code == 200

        self.seller_books = Send_Receive(conf.URL)

        # 付款
        code = self.buyer.payment(self.order_id)
        assert code == 200

        yield

    # 收货
    def test_receive_books_ok(self):
        # 变成已付款
        '''code = self.buyer.payment(self.order_id)
        assert code == 200'''

        # 发货
        code = self.seller_books.send_books(self.seller_id, self.order_id)
        assert code == 200

        # 收货
        code = self.seller_books.receive_books(self.buyer_id, self.order_id)
        assert code == 200

    # order_id 不存在
    def test_invalid_order_id_receive(self):
        # 发货
        code = self.seller_books.send_books(self.seller_id, self.order_id)
        assert code == 200

        code = self.seller_books.receive_books(self.seller_id, self.order_id + 'x')
        assert code != 200

    # user_id 与 store 的 user_id 不对应
    def test_authorization_error_receive(self):
        # 发货
        code = self.seller_books.send_books(self.seller_id, self.order_id)
        assert code == 200

        code = self.seller_books.receive_books(self.seller_id + 'x', self.order_id)
        assert code != 200

    # 未发货，收货报错
    def test_error_unpaid_send(self):
        code = self.seller_books.receive_books(self.buyer_id, self.order_id)
        assert code != 200
