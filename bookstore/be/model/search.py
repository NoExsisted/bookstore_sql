from be.model import db_conn
from be.model import error
import pymysql
import traceback


class Search(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    # store_id 0 表示全局搜索，其他表示店铺 id
    def search_books(self, store_id, search_query, search_scopes) -> (int, str):
        # 1. 有条件有范围
        # 2. 没条件有范围（相当于没条件没范围，比如范围是tags，那么还是返回所有书本）
        # 3. 没条件没范围
        # 4. 有条件没范围
        try:
            cursor = self.conn.cursor()
            query = ""
            choice = []
            if search_query:
                #choice = search_scopes
                if 'title' in search_scopes:
                    query += "title LIKE %s OR "
                    choice.append(f"%{search_query}%")

                if 'author' in search_scopes:
                    query += "author LIKE %s OR "
                    choice.append(f"%{search_query}%")

                if 'tags' in search_scopes:
                    query += "tags LIKE %s OR "
                    choice.append(f"%{search_query}%")

                if 'content' in search_scopes:
                    query += "content LIKE %s OR "
                    choice.append(f"%{search_query}%")

                if 'book_intro' in search_scopes:
                    query += "book_intro LIKE %s OR "
                    choice.append(f"%{search_query}%")

                query = query.rstrip(" OR ")

                if not search_scopes:
                    query = "title LIKE %s OR author LIKE %s OR tags LIKE %s OR content LIKE %s OR book_intro LIKE %s"
                    choice = [f"%{search_query}%" for _ in range(5)]
                    #choice = ["title", "author", "tags", "content", "book_int]

                # 获取总结果数
                if store_id != 0:  # 在店铺范围内搜索
                    choice.append(store_id)
                    cursor.execute(f"SELECT COUNT(*) from store where {query} and store_id = %s;", tuple(choice))
                    '''choice_ = ', '.join(choice)
                    sql_query = (
                            "SELECT COUNT(*) from store WHERE MATCH(" + choice_ + ") AGAINST (%s) "
                            "and store_id = %s;"
                    )
                    cursor.execute(sql_query, (search_query, store_id,))'''
                    total = cursor.fetchone()[0]

                    cursor.execute(f"SELECT title from store where {query} and store_id = %s;", tuple(choice))
                    '''sql_query = (
                            "SELECT title from store WHERE MATCH(" + choice_ + ") AGAINST (%s) "
                            "and store_id = %s;"
                    )
                    cursor.execute(sql_query, (search_query, store_id,))'''
                    book_titles = [book[0] for book in cursor.fetchall()]
                    #print(book_titles)
                else:  # 全局搜索
                    #choice_ = ', '.join(choice)
                    '''sql_query = (
                            "SELECT COUNT(*) from store WHERE MATCH(" + choice_ + ") AGAINST (%s);"
                    )
                    print(sql_query)
                    cursor.execute(sql_query, (search_query,))'''
                    cursor.execute(f"SELECT COUNT(*) from store where {query}", tuple(choice))
                    total = cursor.fetchone()[0]
                    #print("total:", total)

                    cursor.execute(f"SELECT title from store where {query}", tuple(choice))
                    '''cursor.execute(
                        "SELECT title from store WHERE MATCH(" + choice_ + ") AGAINST (%s);",
                        (search_query,)
                    )'''
                    book_titles = [book[0] for book in cursor.fetchall()]
            else:
                if store_id != 0:
                    cursor.execute(f"SELECT COUNT(*) from store where store_id = %s", (store_id,))
                    total = cursor.fetchone()[0]

                    cursor.execute(f"SELECT title from store where store_id = %s", (store_id,))
                    book_titles = [book[0] for book in cursor.fetchall()]
                else:
                    cursor.execute(f"SELECT COUNT(*) from store")
                    total = cursor.fetchone()[0]

                    cursor.execute(f"SELECT title from store")
                    book_titles = [book[0] for book in cursor.fetchall()]

            self.conn.commit()

            if total == 0:
                return error.error_no_eligible_book()
            else:
                result_p = []
                result_t = []
                output = ""
                page_num = int(total / 3)
                if total % 3:
                    page_num += 1
                for page in range(page_num):
                    result_p.append("page" + str(page + 1) + ": " + "\n")
                    result_t.append(book_titles[page * 3: page * 3 + 3])
                for page in range(page_num):
                    output = output + result_p[page] + str(result_t[page]) + "\n"
                f = open('output.txt', 'a+')
                print(output, file=f)
                f.close()
                return 200, str(output)

        except pymysql.Error as e:
            traceback.print_exc()
            #print(e.args[0], e.args[1])
            return 528, "{}".format(str(e))
        except BaseException as e:
            traceback.print_exc()
            return 530, "{}".format(str(e))
