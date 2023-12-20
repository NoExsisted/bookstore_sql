from be.model import db_conn
from be.model import error
import pymysql
import traceback

class Send_Receive(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def send_books(self, user_id: str, order_id: str) -> (int, str):
        try:
            cursor = self.conn.cursor()
            # 找到店家 store_id 和书本状态 book_status
            cursor.execute(
                "SELECT store_id, book_status from new_order_paid where order_id = %s;",
                (order_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            store_id = row[0]
            book_status = row[1]

            # 根据 store_id 在 user_store 表里找到店主 seller_id
            cursor.execute(
                "SELECT user_id from user_store where store_id = %s;",
                (store_id,),
            )
            row = cursor.fetchone()
            # 要不加个外键确保 new_order_paid 里有 store_id，user_store 里一定有
            #if row is None:
            #    return error.error_non_exist_store_id(store_id)

            seller_id = row[0]

            if seller_id != user_id:
                return error.error_authorization_fail()
            # 因为在 new_order_paid 里找的订单，所以一定是已付款，
            # 但防止发货了又发，或者已经收货又发货，再加一个判断
            if book_status != 1:  # (1: 已付款未发货)
                return error.error_book_status()

            # 更新 new_order_paid 表里的 book_status 为 0 （0：已发货）
            cursor.execute(
                "UPDATE new_order_paid set book_status = 0 "
                "where order_id = %s;",
                (order_id),
            )
            self.conn.commit()
        except pymysql.Error as e:
            return 528, "{}".format(str(e))

        return 200, "ok"

    def receive_books(self, user_id: str, order_id: str) -> (int, str):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT user_id, book_status from new_order_paid where order_id = %s;",
                (order_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            buyer_id = row[0]
            book_status = row[1]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            if book_status != 0:
                return error.error_book_status()

            # 更新 new_order_paid 表里的 book_status 为 3 （3：已收货）
            cursor.execute(
                "UPDATE new_order_paid set book_status = 3 "
                "where order_id = %s;",
                (order_id),
            )

            self.conn.commit()

        except pymysql.Error as e:
            #traceback.print_exc()
            return 528, "{}".format(str(e))

        return 200, "ok"
