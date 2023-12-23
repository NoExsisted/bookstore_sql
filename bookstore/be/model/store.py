import logging
import pymysql


class Store:
    database: str

    def __init__(self):
        self.database = pymysql.connect(
            host = '127.0.0.1',  # 数据库主机名
            port = 3306,               # 数据库端口号，默认为3306
            user = 'root',             # 数据库用户名
            password='root',
            db = 'bookstore',               # 数据库名称
            charset = 'utf8'           # 字符编码
        )
        self.init_tables()

    def init_tables(self):
        try:
            conn = self.get_db_conn()
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS user ("
                "user_id VARCHAR(255) PRIMARY KEY, password VARCHAR(255) NOT NULL, "
                "balance INTEGER NOT NULL, token TEXT, terminal VARCHAR(255));"
            )

            cursor.execute(
                "CREATE TABLE IF NOT EXISTS user_store("
                "user_id VARCHAR(255), store_id VARCHAR(255), PRIMARY KEY(user_id, store_id));"
            )

            cursor.execute(
                "CREATE TABLE IF NOT EXISTS store( "
                "store_id VARCHAR(255), book_id VARCHAR(255), book_info MEDIUMTEXT, stock_level INTEGER,"
                " title VARCHAR(255), author VARCHAR(255),"
                " book_intro TEXT, content TEXT,tags VARCHAR(255),"
                " PRIMARY KEY(store_id, book_id), "
                "FULLTEXT(title, author, book_intro, content, tags));"
            )

            cursor.execute(
                "CREATE TABLE IF NOT EXISTS book("
                "store_id VARCHAR(255), "
                "id VARCHAR(255) PRIMARY KEY, title VARCHAR(255), author VARCHAR(255), "
                "publisher VARCHAR(255), original_title VARCHAR(255), "
                "translator VARCHAR(255), pub_year VARCHAR(255),"
                "pages INTEGER, price INTEGER, currency_unit VARCHAR(255),"
                "binding VARCHAR(255), isbn VARCHAR(255),"
                "author_intro TEXT, book_intro TEXT, content TEXT,"
                "tags VARCHAR(255), picture MEDIUMBLOB);"
            )

            cursor.execute(
                "CREATE TABLE IF NOT EXISTS new_order( "
                "order_id VARCHAR(255) PRIMARY KEY, store_id VARCHAR(255), "
                "user_id VARCHAR(255), book_status INTEGER, order_time DATETIME);"
            )

            cursor.execute(
                "CREATE TABLE IF NOT EXISTS new_order_detail( "
                "user_id VARCHAR(255), order_id VARCHAR(255), book_id VARCHAR(255), "
                "count INTEGER, price INTEGER, flag INTEGER, "
                "PRIMARY KEY(order_id, book_id));"
            )

            cursor.execute(
                "CREATE TABLE IF NOT EXISTS new_order_paid( "
                "order_id VARCHAR(255), user_id VARCHAR(255), store_id VARCHAR(255), "
                "book_status INTEGER, price INTEGER, "
                "PRIMARY KEY(order_id, user_id));"
            )

            conn.commit()
        except pymysql.Error as e:
            logging.error(e)
            conn.rollback()

    def get_db_conn(self) -> str:
        return self.database


database_instance = Store()


def init_database():
    global database_instance
    database_instance = Store()


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()

init_database()