import sqlite3

import gc


class SqliteDAO:
    def __init__(self, path, use_cache):
        self.db_path = path
        self.use_cache = use_cache
        self.conn = None

    def start_connect(self):
        self.conn = sqlite3.connect(self.db_path)

    def close_connect(self):
        self.conn.close()

    def _select(self, sql, keys, params):  # 执行查询语句
        sql_cursor = self.conn.cursor()
        # print(params, sql)
        rows = sql_cursor.execute(sql, params)
        result = list()
        for row in rows:
            cols = {_key: row[i] for i, _key in enumerate(keys)}
            result.append(cols)
        return result

    def _execute(self, sql, params):  # 执行增删改语句
        conn = sqlite3.connect(self.db_path)
        sql_cursor = conn.cursor()
        rows = sql_cursor.execute(sql, params)
        conn.commit()
        conn.close()
        return rows
