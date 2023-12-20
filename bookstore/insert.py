import sqlite3
import pymysql

sqlite_conn = sqlite3.connect('./fe/data/book_lx.db')
sqlite_cursor = sqlite_conn.cursor()

mysql_conn = pymysql.connect(
    host='127.0.0.1',  # 数据库主机名
    port=3306,  # 数据库端口号，默认为3306
    user='root',  # 数据库用户名
    password='root',
    database='bookstore',  # 数据库名称
    charset='utf8'  # 字符编码
)
mysql_cursor = mysql_conn.cursor()

# sqlite_cursor.execute('PRAGMA table_info(book)') # 查看列名
# col = sqlite_cursor.fetchall()
# for row in col:
#    print(row[1])
sqlite_cursor.execute('SELECT * FROM book')
# sqlite_cursor.execute('PRAGMA table_info(book)') # 查看列名
data = sqlite_cursor.fetchall()

stores = [1, 1, 1, 2, 2]
auth = []
flag = 0
for row in data:
    if row[2] in auth:
        continue
    else:
        auth.append(row[2])
        flag += 1
        if flag == 6:
            break
    '''print(row)
    for i in range(17):
        print(row[i])
        print('#######################')
    break'''
    row = list(row)
    row.insert(0, stores[flag - 1])
    row = tuple(row)
    mysql_cursor.execute(
        """
        INSERT INTO book (
        store_id, id, title, author, publisher,
        original_title, translator, pub_year,
        pages, price, currency_unit, binding,
        isbn, author_intro, book_intro, content, 
        tags, picture) 
        VALUES (
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s,
        %s, %s, %s)""", row)  # 不存 picture
mysql_conn.commit()

# 关闭连接
sqlite_cursor.close()
sqlite_conn.close()
mysql_cursor.close()
mysql_conn.close()
