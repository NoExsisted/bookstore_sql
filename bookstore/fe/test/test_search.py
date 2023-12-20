import pytest

from fe.access.search import Search
from fe import conf


# bookstore 中的 book 表里已插入 book_lx.db 中的不同作者的五本书
# title 分别是 [撒哈拉的故事, 你是锦瑟 我为流年, 做一个特立独行的女子：三毛传, 奇葩说：爱情需要反复讨论, 楚辞]

class TestSearch:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.search = Search(conf.URL)
        yield

    def test_search_books_ok(self):
        # 撒哈拉的故事，author, book_intro 和 tags 包含“三毛”
        # 你是锦瑟 我为流年，book_intro 和 tags 包含“三毛”
        # 做一个特立独行的女子：三毛传，title, book_intro, content, tags 包含“三毛”
        # 奇葩说：爱情需要反复讨论，不包含“三毛”
        # 楚辞，tags 包含“三毛”
        self.search_query = "三毛"
        self.search_scopes = ["title", "author", "tags", "content", "book_intro"]  # 4
        code, message = self.search.search_books(0, self.search_query, self.search_scopes)
        assert code == 200

        self.search_scopes = ["book_intro"]  # 3
        code, message = self.search.search_books(0, self.search_query, self.search_scopes)
        assert code == 200

        self.search_scopes = ["book_intro"]  # 2
        code, message = self.search.search_books(1, self.search_query, self.search_scopes)
        assert code == 200

        self.search_scopes = ["tags"]  # 4
        code, message = self.search.search_books(0, self.search_query, self.search_scopes)
        assert code == 200

        self.search_scopes = ["content"]  # 1
        code, message = self.search.search_books(0, self.search_query, self.search_scopes)
        assert code == 200

        # 有条件没范围
        self.search_scopes = []  # 4
        code, message = self.search.search_books(0, self.search_query, self.search_scopes)
        assert code == 200

    def test_search_books_ok_no_query(self):
        # 没条件没范围（没条件有范围）
        # 全局搜索
        self.search_query = ""
        self.search_scopes = []  # 5
        code, message = self.search.search_books(0, self.search_query, self.search_scopes)
        assert code == 200

        # 没条件没范围（没条件有范围）
        # 店铺搜索
        self.search_query = ""
        self.search_scopes = []  # 3
        code, message = self.search.search_books(1, self.search_query, self.search_scopes)
        assert code == 200

    # total = 0，即没有找到符合条件的书
    def test_search_books_no_book(self):
        self.search_query = "余华"
        self.search_scopes = []
        code, message = self.search.search_books(0, self.search_query, self.search_scopes)
        assert code == 525
