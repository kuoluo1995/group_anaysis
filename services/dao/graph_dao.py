import queue
import networkx as nx
from collections import defaultdict

from services.dao.base_dao import SqliteDAO


class GraphDAO(SqliteDAO):
    def __init__(self, path, use_cache=True):
        super().__init__(path, use_cache)
        self.node_id2code_cache = {}
        self.node_id2name_cache = {}
        self.node_id2label_cache = {}
        self.node_name2ids_cache = defaultdict(list)
        self.node_label_code2id_cache = defaultdict(dict)

        self.in_edge_cache = {}
        self.out_edge_cache = {}
        self.edge_label_cache = {}
        if self.use_cache:
            self.__import_all_data()

    def __import_all_data(self):
        sql_str = '''SELECT DISTINCT id, name, code, label FROM node2data'''
        rows = self._select(sql_str, ['id', 'name', 'code', 'label'], ())
        for cols in rows:
            self.node_id2label_cache[cols['id']] = str(cols['label'])
            self.node_id2name_cache[cols['id']] = str(cols['name'])
            self.node_name2ids_cache[str(cols['name'])].append(cols['id'])

    def get_node_ids_by_label_codes(self, node_label, node_codes):  # label里不包含年份，因为年份没有code
        new_codes = [_code for _code in node_codes if _code not in self.node_label_code2id_cache[node_label]]
        if len(new_codes) > 0:
            sql_str = '''SELECT DISTINCT id, name, code FROM node2data WHERE label = ? AND code in {}'''.format(
                tuple(new_codes) if len(new_codes) > 1 else "({})".format(new_codes[0]))
            rows = self._select(sql_str, ['id', 'name', 'code'], (node_label,))
            if not self.use_cache:
                return [cols['id'] for cols in rows]
            for cols in rows:
                self.node_id2code_cache[cols['id']] = int(cols['code'])
                self.node_id2label_cache[cols['id']] = str(node_label)
                self.node_id2name_cache[cols['id']] = str(cols['name'])
                self.node_label_code2id_cache[node_label][int(cols['code'])] = cols['id']
        return [int(self.node_label_code2id_cache[node_label][_code]) for _code in node_codes if
                _code in self.node_label_code2id_cache[node_label]]

    def get_node_code_by_id(self, node_id):
        if node_id not in self.node_id2code_cache:
            sql_str = '''SELECT name, label, code FROM node2data WHERE id = ?'''
            rows = self._select(sql_str, ['name', 'label', 'code'], (node_id,))
            if not self.use_cache:
                return int(rows[0]['code'])
            self.node_id2code_cache[node_id] = int(rows[0]['code'])
            self.node_id2label_cache[node_id] = str(rows[0]['label'])
            self.node_id2name_cache[node_id] = str(rows[0]['name'])
            self.node_label_code2id_cache[str(rows[0]['label'])][int(rows[0]['code'])] = node_id
        return self.node_id2code_cache[node_id]

    def get_node_name_by_id(self, node_id):
        if node_id not in self.node_id2name_cache:
            sql_str = '''SELECT name, label, code FROM node2data WHERE id = ?'''
            rows = self._select(sql_str, ['name', 'label', 'code'], (node_id,))
            if not self.use_cache:
                return str(rows[0]['name'])
            self.node_id2label_cache[node_id] = str(rows[0]['label'])
            self.node_id2name_cache[node_id] = str(rows[0]['name'])
        return self.node_id2name_cache[node_id]

    def get_node_label_by_id(self, node_id):
        if node_id not in self.node_id2label_cache:
            sql_str = '''SELECT name, label, code FROM node2data WHERE id = ?'''
            rows = self._select(sql_str, ['name', 'label', 'code'], (node_id,))
            if not self.use_cache:
                return str(rows[0]['label'])
            self.node_id2label_cache[node_id] = str(rows[0]['label'])
            self.node_id2name_cache[node_id] = str(rows[0]['name'])
        return self.node_id2label_cache[node_id]

    def get_edge_label_by_id(self, edge_id):
        if edge_id not in self.edge_label_cache:
            sql_str = '''SELECT label FROM rel2data WHERE id = ?'''
            rows = self._select(sql_str, ['label'], (edge_id,))
            if not self.use_cache:
                return str(rows[0]['label'])
            self.edge_label_cache[edge_id] = str(rows[0]['label'])
        return self.edge_label_cache[edge_id]

    def get_node_ids_by_name(self, node_name):  # 非年份的所有结点
        if node_name not in self.node_name2ids_cache:
            sql_str = '''SELECT id, label, code FROM node2data WHERE name = ?'''
            rows = self._select(sql_str, ['id', 'label', 'code'], (node_name,))
            if not self.use_cache:
                return [cols['id'] for cols in rows]
            for cols in rows:
                self.node_id2code_cache[cols['id']] = int(cols['code'])
                self.node_id2label_cache[cols['id']] = str(cols['label'])
                self.node_id2name_cache[cols['id']] = str(node_name)
                self.node_label_code2id_cache[str(cols['label'])][int(cols['code'])] = cols['id']
                self.node_name2ids_cache[node_name].append(cols['id'])
        return self.node_name2ids_cache[node_name]

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
        used_children_nodes = set()
        while not node_queue.empty():
            _item = node_queue.get()
            now_node, now_depth = _item['node_id'], _item['depth']
            if now_node in used_nodes or now_depth >= max_depth:  # 遍历过的点不要
                continue
            used_nodes.add(now_node)
            children_nodes = [_item['target_id'] for _item in self.get_out_edges(now_node)]
            for _node in children_nodes:
                if _node not in used_nodes and now_depth < max_depth and _node not in used_children_nodes:
                    node_queue.put({'node_id': _node, 'depth': now_depth + 1})
                    used_children_nodes.add(_node)

        sub_graph = nx.MultiDiGraph()
        for _node in used_nodes:
            for _item in self.get_out_edges(_node):
                if _item['target_id'] in used_nodes:
                    sub_graph.add_edge(_item['source_id'], _item['target_id'], r_id=_item['edge_id'])
        return sub_graph


if __name__ == '__main__':
    graph_dao = GraphDAO('../../dataset/graph.db', use_cache=True)
    print(1)
