import queue
import sqlite3
import networkx as nx


class SqliteGraphDAO:
    def __init__(self):
        self.db_path = './dataset/graph.db'
        self.use_cache = True
        self.node_name2id_cache = {}
        self.node_id2name_cache = {}
        self.node_id2label_cache = {}

        self.in_edge_cache = {}
        self.out_edge_cache = {}
        self.edge_label_cache = {}

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

    def get_edge_label_by_id(self, edge_id):
        if edge_id not in self.edge_label_cache:
            rows = self._select('''SELECT label FROM rel2data WHERE id = ?''', ['label'], (edge_id,))
            if not self.use_cache:
                return rows[0]['label']
            self.edge_label_cache[edge_id] = rows[0]['label']
        return self.edge_label_cache[edge_id]

    def get_in_edges(self, target_id):
        if target_id not in self.in_edge_cache:
            rows = self._select('''SELECT source, r_id FROM graph WHERE target = ?''', ['source', 'r_id'], (target_id,))
            rows = [{'source_id': row['source'], 'target_id': target_id, 'edge_id': row['r_id']} for row in rows]
            if not self.use_cache:
                return rows
            self.in_edge_cache[target_id] = rows
        return self.in_edge_cache[target_id]

    def get_out_edges(self, source_id):
        if source_id not in self.out_edge_cache:
            rows = self._select('''SELECT target, r_id FROM graph WHERE source = ?''', ['target', 'r_id'], (source_id,))
            rows = [{'source_id': source_id, 'target_id': row['target'], 'edge_id': row['r_id']} for row in rows]
            if not self.use_cache:
                return rows
            self.out_edge_cache[source_id] = rows
        return self.out_edge_cache[source_id]

    def get_sub_graph(self, node_id, max_depth=2):
        node_queue = queue.Queue()  # 宽度搜索
        node_queue.put({'node_id': node_id, 'depth': 0})
        used_nodes = set()  # stack
        while not node_queue.empty():
            _item = node_queue.get()
            now_node, now_depth = _item['node_id'], _item['depth']
            if now_node in used_nodes:  # 遍历过的点不要
                continue
            used_nodes.add(now_node)
            children_nodes = [_item['target_id'] for _item in self.get_out_edges(now_node)]
            for _node in children_nodes:
                if _node not in used_nodes and now_depth < max_depth:
                    node_queue.put({'node_id': _node, 'depth': now_depth + 1})

        sub_graph = nx.MultiDiGraph()
        for _node in used_nodes:
            for _item in self.get_out_edges(_node):
                if _item['target_id'] in used_nodes:
                    sub_graph.add_edge(_item['source_id'], _item['target_id'], r_id=_item['edge_id'])
        return sub_graph
