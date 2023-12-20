import uuid
import json
from be.model import db_conn
from be.model import error
import pymysql
import traceback
from datetime import datetime


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            cursor = self.conn.cursor()
            for book_id, count in id_and_count:
                cursor = self.conn.cursor()
                cursor.execute(
                    "SELECT book_id, stock_level, book_info FROM store "
                    "WHERE store_id = %s AND book_id = %s;",
                    (store_id, book_id),
                )
                row = cursor.fetchone()
                if row is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = row[1]
                book_info = row[2]
                book_info_json = json.loads(book_info)
                price = book_info_json.get("price")

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                cursor = self.conn.cursor()
                cursor.execute(
                    "UPDATE store set stock_level = stock_level - %s "
                    "WHERE store_id = %s and book_id = %s and stock_level >= %s; ",
                    (count, store_id, book_id, count),
                )
                if cursor.rowcount == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)

                # 为了订单取消能恢复，后续不删除 new_order_detail，而是增加一个 flag，0 正常，1 付款，2 取消
                cursor.execute(
                    "INSERT INTO new_order_detail("
                    "user_id, order_id, book_id, count, price, flag) "
                    "VALUES(%s, %s, %s, %s, %s, 0);",
                    (user_id, uid, book_id, count, price),
                )

            '''cursor.execute(
                "INSERT INTO new_order(order_id, store_id, user_id) "
                "VALUES(%s, %s, %s);",
                (uid, store_id, user_id),
            )'''
            # book_status: 2 表示未付款
            current = datetime.now()
            cursor.execute(
                "INSERT INTO new_order(order_id, store_id, user_id, book_status, order_time) "
                "VALUES(%s, %s, %s, 2, %s);",
                (uid, store_id, user_id, current),
            )

            self.conn.commit()
            order_id = uid
        except pymysql.Error as e:
            #logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            #logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        conn = self.conn
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT order_id, store_id, user_id FROM new_order WHERE order_id = %s;",
                (order_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            order_id = row[0]
            store_id = row[1]
            buyer_id = row[2]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            cursor.execute(
                "SELECT balance, password FROM user WHERE user_id = %s;", (buyer_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row[0]
            if password != row[1]:
                return error.error_authorization_fail()

            cursor.execute(
                "SELECT store_id, user_id FROM user_store WHERE store_id = %s;",
                (store_id,),
            )
            row = cursor.fetchone()

            seller_id = row[1]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            cursor.execute(
                "SELECT book_id, count, price FROM new_order_detail WHERE order_id = %s;",
                (order_id,),
            )
            total_price = 0
            for row in cursor:
                count = row[1]
                price = row[2]
                total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            cursor.execute(
                "UPDATE user set balance = balance - %s "
                "WHERE user_id = %s AND balance >= %s;",
                (total_price, buyer_id, total_price),
            )
            if cursor.rowcount == 0:
                return error.error_not_sufficient_funds(order_id)

            cursor.execute(
                "UPDATE user set balance = balance + %s " 
                "WHERE user_id = %s;",
                (total_price, seller_id),
            )

            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(seller_id)

            # 支付后从 new_order 删除
            cursor.execute(
                "DELETE FROM new_order WHERE order_id = %s;", (order_id,)
            )
            #if cursor.rowcount == 0:
            #    return error.error_invalid_order_id(order_id)
            # payment 一开始已经检查过了 order_id

            '''cursor.execute(
                "DELETE FROM new_order_detail where order_id = %s;", (order_id,)
            )
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)'''
            # 为了订单取消能恢复，不删除 new_order_detail，而是增加一个 flag，0 正常，1 支付，2 取消
            cursor.execute(
                "UPDATE new_order_detail SET flag = 1 WHERE order_id = %s",
                (order_id,),
            )
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            cursor.execute(
                "INSERT INTO new_order_paid ("
                "order_id, user_id, store_id, "
                "book_status, price) "
                "VALUES (%s, %s, %s, 1, %s);",  # 1 是已付款未发货
                (order_id, buyer_id, store_id, total_price)
            )

            conn.commit()

        except pymysql.Error as e:
            #traceback.print_exc()
            #print(e.args[0], e.args[1])
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT password from user where user_id=%s", (user_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail()

            if row[0] != password:
                return error.error_authorization_fail()

            cursor.execute(
                "UPDATE user SET balance = balance + %s WHERE user_id = %s",
                (add_value, user_id),
            )
            # 前面已经从 user 表中找到了，不用再检查了
            #if cursor.rowcount == 0:
            #    return error.error_non_exist_user_id(user_id)

            self.conn.commit()
        except pymysql.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
