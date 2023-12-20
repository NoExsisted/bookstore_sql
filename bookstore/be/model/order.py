from be.model import db_conn
from be.model import error
import pymysql
import traceback
from datetime import datetime


class Order(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    # 买家取消订单，手动取消
    def new_order_cancel_manually(self, user_id: str, order_id: str) -> (int, str):
        try:
            cur = self.conn.cursor()
            cursor = self.conn.cursor()
            cursor.execute("SELECT user_id from new_order where order_id = %s;",
                           (order_id,))
            row = cursor.fetchone()

            # 没支付，取消后从 new_order 删除
            if row is not None:
                buyer_id = row[0]

                if buyer_id != user_id:
                    return error.error_authorization_fail()

                cursor.execute(
                    "DELETE FROM new_order WHERE order_id = %s;", (order_id,)
                )

                '''cursor.execute(
                    "DELETE FROM new_order_detail where order_id = %s;", (order_id,)
                )
                if cursor.rowcount == 0:
                    return error.error_invalid_order_id(order_id)'''
                cursor.execute(
                    "UPDATE new_order_detail SET flag = 2 WHERE order_id = %s",
                    (order_id,),
                )
            # 如果已支付，将金额退回买家，卖家余额减少
            # 通过 store_id，在 user_store 表中找到卖家
            else:
                cursor.execute("SELECT user_id, store_id, price from new_order_paid "
                               "where order_id = %s;",
                               (order_id,))
                row = cursor.fetchone()
                if row is None:
                    return error.error_invalid_order_id(order_id)

                buyer_id = row[0]  # 买家
                store_id = row[1]
                price = row[2]

                if buyer_id != user_id:
                    return error.error_authorization_fail()

                # 从 new_order_paid 里获得的 store_id 一定是存在的
                cursor.execute(
                    "SELECT user_id FROM user_store WHERE store_id = %s;",
                    (store_id,),
                )
                row = cursor.fetchone()

                seller_id = row[0]  # 卖家

                # 减少卖家余额
                cursor.execute(
                    "UPDATE user SET balance = balance - %s WHERE user_id = %s",
                    (price, seller_id)
                )

                # 增加买家余额
                cursor.execute(
                    "UPDATE user SET balance = balance + %s WHERE user_id = %s",
                    (price, buyer_id)
                )

                # 从 new_order_paid 删除订单
                cursor.execute("DELETE FROM new_order_paid WHERE order_id = %s", (order_id,))

                # 增加库存
                cursor.execute(
                    "SELECT book_id, count FROM new_order_detail WHERE order_id = %s;",
                    (order_id,),
                )
                for row in cursor:
                    book_id = row[0]
                    count = row[1]
                    cur.execute(
                        "UPDATE store SET stock_level = stock_level + %s WHERE store_id = %s AND book_id = %s",
                        (count, store_id, book_id)
                    )

                    cur.execute(
                        "UPDATE new_order_detail SET flag = 2 WHERE order_id = %s",
                        (order_id,),
                    )

            self.conn.commit()
            return 200, "ok"
        except pymysql.Error as e:
            #traceback.print_exc()
            #print(e.args[0], e.args[1])
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

    # 订单超时未被支付自动取消
    def new_order_cancel_auto(self, order_id: str) -> (int, str):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT order_time from new_order where order_id = %s;",
                           (order_id,))
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)
            order_time = row[0]
            current = datetime.now()
            delta = current - order_time

            # 如果超过 5s 没有付款，自动取消订单
            if delta.seconds > 5:
                cursor.execute(
                    "DELETE FROM new_order WHERE order_id = %s;", (order_id,)
                )

                cursor.execute(
                    "UPDATE new_order_detail SET flag = 2 WHERE order_id = %s",
                    (order_id,),
                )

            self.conn.commit()
            return 200, "ok"
        except pymysql.Error as e:
            #traceback.print_exc()
            #print(e.args[0], e.args[1])
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

    def query_order_history(self, user_id: str) -> (int, str):
        try:
            cursor = self.conn.cursor()
            # 支付后删除了 new_order 所以找不到
            cursor.execute("SELECT * from new_order_detail where user_id = %s;",
                           (user_id,))
            unpaid_history = []
            paid_history = []
            canceled_history = []

            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(user_id)

            i = 0
            temp = ""
            books = []
            counts = []
            prices = []
            for row in cursor:

                order_id = row[1]
                book_id = row[2]
                count = row[3]
                price = row[4]
                flag = row[5]
                if i == 0:
                    temp = order_id

                if order_id == temp and i != (cursor.rowcount - 1):
                    books.append(book_id)
                    counts.append(count)
                    prices.append(price)
                else:
                    info = {
                        'order_id': order_id,
                        'book_id': books,
                        'count': counts,
                        'price': prices,
                        'buyer_id': user_id,
                    }

                    books = []
                    counts = []
                    prices = []

                    if flag == 0:
                        unpaid_history.append(info)
                    elif flag == 1:
                        paid_history.append(info)
                    elif flag == 2:
                        canceled_history.append(info)

                temp = order_id
                i += 1

            output = {'unpaid': unpaid_history,
                      'paid': paid_history,
                      'canceled': canceled_history}
            f = open('output2.txt', 'a+')
            print(output, file=f)
            f.close()

            self.conn.commit()
            return 200, "ok"
        except pymysql.Error as e:
            #traceback.print_exc()
            #print(e.args[0], e.args[1])
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
