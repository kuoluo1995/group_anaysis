import sqlite3
import networkx as nx
from queue import Queue


class SqliteGraph:
    def __init__(self):
        self.db_path = './dataset/graph.db'
        self.use_cache = True
        self.node_name2id_cache = {}
        self.node_id2name_cache = {}
        self.node_id2label_cache = {}

        self.in_relation_cache = {}
        self.out_relation_cache = {}

    def _select(self, sql, keys, params):
        conn = sqlite3.connect(self.db_path)
        sql_cursor = conn.cursor()
        rows = sql_cursor.execute(sql, params)
        result = list()
        for row in rows:
            temp = {}
            for i, _key in enumerate(keys):
                temp.update({_key: row[i]})
            result.append(temp)
        conn.close()
        return result

    def _execute(self, sql, params):
        conn = sqlite3.connect(self.db_path)
        sql_cursor = conn.cursor()
        rows = sql_cursor.execute(sql, params)
        conn.commit()
        conn.close()
        return rows

    def get_node_id_by_name(self, node_name):
        if node_name not in self.node_name2id_cache:
            rows = self._select('''SELECT id FROM node2data WHERE name = ?''', ['id'], (node_name,))
            if not self.use_cache:
                return rows[0]['id']
            self.node_name2id_cache[node_name] = rows[0]['id']
        return self.node_name2id_cache[node_name]

    def get_node_name_by_id(self, node_id):
        if node_id not in self.node_id2name_cache:
            rows = self._select('''SELECT name FROM node2data WHERE id = ?''', ['name'], (node_id,))
            if not self.use_cache:
                return rows[0]['name']
            self.node_id2name_cache[node_id] = rows[0]['name']
        return self.node_id2name_cache[node_id]

    def get_node_label_by_id(self, node_id):
        if node_id not in self.node_id2label_cache:
            rows = self._select('''SELECT label FROM node2data WHERE id = ?''', ['label'], (node_id,))
            if not self.use_cache:
                return rows[0]['label']
            self.node_id2label_cache[node_id] = rows[0]['label']
        return self.node_id2label_cache[node_id]

    def get_in_relations(self, target_id):
        if target_id not in self.in_relation_cache:
            rows = self._select('''SELECT source, r_id FROM graph WHERE target = ?''', ['source', 'r_id'], (target_id,))
            rows = [(row['source'], target_id, row['r_id']) for row in rows]
            if not self.use_cache:
                return rows
            self.in_relation_cache[target_id] = rows
        return list(self.in_relation_cache[target_id])

    def get_out_relations(self, source_id):
        if source_id not in self.out_relation_cache:
            rows = self._select('''SELECT target, r_id FROM graph WHERE source = ?''', ['target', 'r_id'], (source_id,))
            rows = [(source_id, row['target'], row['r_id']) for row in rows]
            if not self.use_cache:
                return rows
            self.out_relation_cache[source_id] = rows
        return self.out_relation_cache[source_id]

    def get_relation(self, node_id):
        return self.get_in_relations(node_id) + self.get_out_relations(node_id)

    def get_out_nodes(self, node_id):
        return [target for source, target, r_id in self.get_out_relations(node_id)]

    # 还需要清理下边， 我猜我这个sub_graph有问题 todo 看一下？我的写法可以吗？
    def get_sub_graph(self, node_id, depth=2):
        node_queue = {node_id: 0}
        used_nodes = set()

        while len(node_queue) > 0:
            now_node, now_depth = node_queue.popitem()
            used_nodes.add(now_node)
            # next_depth = node2depth[now_node] + 1
            children_nodes = self.get_out_nodes(now_node)
            for _node in children_nodes:
                if _node not in used_nodes and _node not in node_queue.keys() and now_depth < depth:
                    node_queue.update({_node: now_depth + 1})

        sub_graph = nx.MultiDiGraph()
        for _node in used_nodes:
            for source, target, r_id in self.get_out_relations(_node):
                if target in used_nodes:
                    sub_graph.add_edge(source, target, r_id=r_id)
        return sub_graph


sqlite_graph = SqliteGraph()
