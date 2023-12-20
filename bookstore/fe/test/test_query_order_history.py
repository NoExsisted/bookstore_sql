import pytest

from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.order import Order
from fe.access.book import Book
from fe import conf
import uuid
from time import sleep


class TestQueryOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_query_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_query_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_query_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        gen_book = GenBook(self.seller_id, self.store_id)
        self.seller = gen_book.seller  # 卖家

        ok, self.buy_book_id_list = gen_book.gen(
            non_exist_book_id=False,
            low_stock_level=False,
            max_book_count=10
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

        code = self.buyer.add_funds(self.total_price)  # 增加余额
        assert code == 200

        self.order = Order(conf.URL)
        yield

    def test_query_order_history_unpaid_ok(self):
        code = self.order.query_order_history(self.buyer_id)
        assert code == 200

    def test_query_order_history_paid_ok(self):
        # 付款记录
        code = self.buyer.payment(self.order_id)
        assert code == 200

        code = self.order.query_order_history(self.buyer_id)
        assert code == 200

    def test_query_order_history_unpaid_cancel_ok(self):
        # 未付款取消
        code = self.order.new_order_cancel_manually(self.buyer_id, self.order_id)
        assert code == 200

        code = self.order.query_order_history(self.buyer_id)
        assert code == 200

    def test_query_order_history_paid_cancel_ok(self):
        # 已付款取消
        code = self.buyer.payment(self.order_id)
        assert code == 200

        code = self.order.new_order_cancel_manually(self.buyer_id, self.order_id)
        assert code == 200

        code = self.order.query_order_history(self.buyer_id)
        assert code == 200

    def test_query_order_history_auto_cancel_ok(self):
        sleep(10)
        code = self.order.new_order_cancel_auto(self.order_id)
        assert code == 200

        code = self.order.query_order_history(self.buyer_id)
        assert code == 200

    # 用户不存在
    def test_error_user_id(self):
        code = self.order.query_order_history(self.buyer_id + "_x")
        assert code == 511
