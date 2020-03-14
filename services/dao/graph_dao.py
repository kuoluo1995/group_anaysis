import gc
import queue
import timeit

import networkx as nx
from collections import defaultdict

from services.dao.base_dao import SqliteDAO
import json


class GraphDAO(SqliteDAO):
    def __init__(self, path, use_cache=True):
        super().__init__(path, use_cache)
        self.node_id2code_cache = {}
        self.node_id2name_cache = {}
        self.node_id2en_name_cache = {}
        self.node_id2label_cache = {}
        self.node_label_code2id_cache = defaultdict(dict)

        self.in_edge_cache = {}
        self.out_edge_cache = {}
        self.edge_label_cache = {}
        self.edge_name_cache = {}
        self.edge_en_name_cache = {}

        self.nid2has_topic_p_cache = {}
        if self.use_cache:  # todo 如果电脑性能允许的话，为了加快运行速度可以考虑提前载入数据
            self.start_connect()
            self.__import_all_data()
            self.close_connect()

    def getAllPersons(self):
        self.start_connect()
        rows = self.conn.cursor().execute('''SELECT id FROM node2data WHERE label = "Person"''')
        result = [row[0] for row in rows]
        self.close_connect()
        return result
    
    # siwei: 找到描述中包含节点的人(必须是总描述数量超过5个的人)
    def getHasNodePeople(self, nid):
        nid2has_topic_p_cache = self.nid2has_topic_p_cache
        
        if nid not in nid2has_topic_p_cache:
            # print((nid, ))
            rows = self._select("SELECT pids FROM reverse_index_person_5 WHERE name = ?", ['pids'], (nid, ))
            if len(rows) == 0:
                print(nid, self.get_node_name_by_id(nid) ,'没有对应的pids')
                # raise Exception(nid, name, '没有对应的pids')
                pids = []
            else:
                # print(1, rows)
                pids = rows[0]['pids']
                pids = list(json.loads(pids).keys())
                pids = set([int(pid) for pid in pids])
            if not self.use_cache:
                return pids
            nid2has_topic_p_cache[nid] = pids
        return list(nid2has_topic_p_cache[nid])


    def __import_all_data(self):
        sql_str = '''SELECT DISTINCT id, name, code, label, en_name FROM node2data'''
        rows = self._select(sql_str, ['id', 'name', 'code', 'label', 'en_name'], ())
        for cols in rows:
            self.node_id2label_cache[int(cols['id'])] = str(cols['label'])
            self.node_id2name_cache[int(cols['id'])] = str(cols['name'])
            self.node_id2en_name_cache[int(cols['id'])] = str(cols['en_name'])

    def get_node_ids_by_label_codes(self, node_label, node_codes):  # label里不包含年份，因为年份没有code
        if len(node_codes) > 0:
            node_codes = [int(_code) for _code in node_codes]
        new_codes = [_code for _code in node_codes if _code not in self.node_label_code2id_cache[node_label]]
        # new_codes = node_codes
        if len(new_codes) > 0:
            sql_str = '''SELECT DISTINCT id, name, code, en_name FROM node2data WHERE label = ? AND code in {}'''.format(
                tuple(new_codes) if len(new_codes) > 1 else "({})".format(new_codes[0]))
            rows = self._select(sql_str, ['id', 'name', 'code', 'en_name'], (node_label,))
            if not self.use_cache:
                return [int(cols['id']) for cols in rows]
            for cols in rows:
                self.node_id2code_cache[int(cols['id'])] = int(cols['code'])
                self.node_id2label_cache[int(cols['id'])] = str(node_label)
                self.node_id2name_cache[int(cols['id'])] = str(cols['name'])
                self.node_id2en_name_cache[int(cols['id'])] = str(cols['en_name'])
                self.node_label_code2id_cache[node_label][int(cols['code'])] = int(cols['id'])

        return [self.node_label_code2id_cache[node_label][int(_code)] for _code in node_codes if
                _code in self.node_label_code2id_cache[node_label]]

    def get_node_code_by_id(self, node_id):
        # node_id = int(node_id)
        if node_id not in self.node_id2code_cache:
            sql_str = '''SELECT name, label, code, en_name FROM node2data WHERE id = ?'''
            rows = self._select(sql_str, ['name', 'label', 'code', 'en_name'], (node_id,))
            if not self.use_cache:
                return int(rows[0]['code'])
            self.node_id2code_cache[node_id] = int(rows[0]['code'])
            self.node_id2label_cache[node_id] = str(rows[0]['label'])
            self.node_id2name_cache[node_id] = str(rows[0]['name'])
            self.node_id2en_name_cache[node_id] = str(rows[0]['en_name'])
            self.node_label_code2id_cache[str(rows[0]['label'])][int(rows[0]['code'])] = node_id
        return self.node_id2code_cache[node_id]

    def get_node_name_by_id(self, node_id):
        node_id = int(node_id)
        if node_id not in self.node_id2name_cache:
            sql_str = '''SELECT name, label, code, en_name FROM node2data WHERE id = ?'''
            rows = self._select(sql_str, ['name', 'label', 'code', 'en_name'], (node_id,))
            if not self.use_cache:
                return str(rows[0]['name'])
            self.node_id2label_cache[node_id] = str(rows[0]['label'])
            self.node_id2name_cache[node_id] = str(rows[0]['name'])
            self.node_id2en_name_cache[node_id] = str(rows[0]['en_name'])
        return self.node_id2name_cache[node_id]

    def get_node_en_name_by_id(self, node_id):
        # node_id = int(node_id)
        if node_id not in self.node_id2en_name_cache:
            sql_str = '''SELECT name, label, code, en_name FROM node2data WHERE id = ?'''
            rows = self._select(sql_str, ['name', 'label', 'code', 'en_name'], (node_id,))
            if not self.use_cache:
                return str(rows[0]['en_name'])
            self.node_id2label_cache[node_id] = str(rows[0]['label'])
            self.node_id2name_cache[node_id] = str(rows[0]['name'])
            self.node_id2en_name_cache[node_id] = str(rows[0]['en_name'])
        return self.node_id2en_name_cache[node_id]

    def get_node_label_by_id(self, node_id):
        # node_id = int(node_id)
        if node_id not in self.node_id2label_cache:
            sql_str = '''SELECT name, label, code, en_name FROM node2data WHERE id = ?'''
            rows = self._select(sql_str, ['name', 'label', 'code', 'en_name'], (node_id,))
            if not self.use_cache:
                return str(rows[0]['label'])
            self.node_id2label_cache[node_id] = str(rows[0]['label'])
            self.node_id2name_cache[node_id] = str(rows[0]['name'])
            self.node_id2en_name_cache[node_id] = str(rows[0]['en_name'])
        return self.node_id2label_cache[node_id]

    def get_node_ids_by_name(self, node_name):  # 非年份的所有结点
        sql_str = '''SELECT id, label, code, en_name FROM node2data WHERE name = ?'''
        rows = self._select(sql_str, ['id', 'label', 'code', 'en_name'], (node_name,))
        return [int(cols['id']) for cols in rows]

    def get_edge_label_by_id(self, edge_id):
        # edge_id = int(edge_id)
        if edge_id not in self.edge_label_cache:
            sql_str = '''SELECT label, name, en_name FROM rel2data WHERE id = ?'''
            rows = self._select(sql_str, ['label', 'name', 'en_name'], (edge_id,))
            if not self.use_cache:
                return str(rows[0]['label'])
            self.edge_label_cache[edge_id] = str(rows[0]['label'])
            self.edge_name_cache[edge_id] = str(rows[0]['name'])
            self.edge_en_name_cache[edge_id] = str(rows[0]['en_name'])
        return self.edge_label_cache[edge_id]

    def get_edge_name_by_id(self, edge_id):
        # edge_id = int(edge_id)
        if edge_id not in self.edge_label_cache:
            sql_str = '''SELECT label, name, en_name FROM rel2data WHERE id = ?'''
            rows = self._select(sql_str, ['label', 'name', 'en_name'], (edge_id,))
            if not self.use_cache:
                return str(rows[0]['name'])
            self.edge_label_cache[edge_id] = str(rows[0]['label'])
            self.edge_name_cache[edge_id] = str(rows[0]['name'])
            self.edge_en_name_cache[edge_id] = str(rows[0]['en_name'])
        return self.edge_name_cache[edge_id]

    def get_edge_en_name_by_id(self, edge_id):
        # edge_id = int(edge_id)
        if edge_id not in self.edge_label_cache:
            sql_str = '''SELECT label, name, en_name FROM rel2data WHERE id = ?'''
            rows = self._select(sql_str, ['label', 'name', 'en_name'], (edge_id,))
            if not self.use_cache:
                return str(rows[0]['en_name'])
            self.edge_label_cache[edge_id] = str(rows[0]['label'])
            self.edge_name_cache[edge_id] = str(rows[0]['name'])
            self.edge_en_name_cache[edge_id] = str(rows[0]['en_name'])
        return self.edge_en_name_cache[edge_id]

    def get_in_edges(self, target_id):
        # target_id = int(target_id)
        if target_id not in self.in_edge_cache:
            rows = self._select('''SELECT source, r_id FROM graph WHERE target = ?''', ['source', 'r_id'], (target_id,))
            # rows = [{'source_id': int(row['source']), 'target_id': target_id, 'edge_id': int(row['r_id'])} for row in
            #         rows]
            rows = [(int(row['source']), target_id, int(row['r_id'])) for row in rows]  # 减小内存消耗
            if not self.use_cache:
                return rows
            self.in_edge_cache[target_id] = rows
        return self.in_edge_cache[target_id]

    def get_out_edges(self, source_id):
        # source_id = int(source_id)
        if source_id not in self.out_edge_cache:
            rows = self._select('''SELECT target, r_id FROM graph WHERE source = ?''', ['target', 'r_id'], (source_id,))
            rows = [(source_id, int(row['target']), int(row['r_id'])) for row in rows]
            if not self.use_cache:
                return rows
            self.out_edge_cache[source_id] = rows
        return self.out_edge_cache[source_id]

    def get_sub_graph(self, node_id, max_depth=3):  # 我的实现方式慢一些，可能由于Queue这里线程安全的缘故？
        start = timeit.default_timer()
        # node_id = int(node_id)
        node_queue = queue.Queue()  # 宽度搜索
        node_queue.put({'node_id': node_id, 'depth': 0})
        used_nodes = set()  # stack
        used_nodes.add(node_id)
        while not node_queue.empty():
            _item = node_queue.get()
            now_node, now_depth = _item['node_id'], _item['depth']
            children_nodes = [_item[1] for _item in self.get_out_edges(now_node)]
            for _node in children_nodes:
                if _node not in used_nodes and now_depth + 1 < max_depth:
                    node_queue.put({'node_id': _node, 'depth': now_depth + 1})
                    used_nodes.add(_node)

        sub_graph = nx.MultiDiGraph()
        for _node in used_nodes:
            for _source_id, _target_id, _edge_id in self.get_out_edges(_node):
                if _target_id in used_nodes:
                    sub_graph.add_edge(_source_id, _target_id, r_id=_edge_id)

        print('时间:{},点数:{}'.format(timeit.default_timer() - start, len(sub_graph.nodes)))
        return sub_graph

    def getSubGraph(self, n_id, depth=3):  # 学长的实现方式快一些，可能由于原生导致的
        start = timeit.default_timer()
        pop_nodes = set([n_id])
        used_nodes = set()

        node2depth = {
            n_id: 0
        }
        while len(pop_nodes) != 0:
            now_node = pop_nodes.pop()
            used_nodes.add(now_node)
            next_depth = node2depth[now_node] + 1

            nei_nodes = [_target_id for _source_id, _target_id, _edge_id in self.get_out_edges(now_node)]
            for nei_node in nei_nodes:
                if nei_node not in used_nodes and nei_node not in pop_nodes and next_depth < depth:
                    pop_nodes.add(nei_node)
                    node2depth[nei_node] = next_depth

                elif nei_node in node2depth and node2depth[nei_node] > next_depth:
                    node2depth[nei_node] = next_depth
                    if next_depth < depth and nei_node in used_nodes:
                        pop_nodes.add(nei_node)
                        used_nodes.remove(nei_node)

        sub_g = nx.MultiDiGraph()
        for node in used_nodes:
            for _source_id, _target_id, _edge_id in self.get_out_edges(node):
                if _target_id in used_nodes:
                    sub_g.add_edge(_source_id, _target_id, r_id=_edge_id)
        # del used_nodes
        # gc.collect()
        print('时间:{},点数:{}'.format(timeit.default_timer() - start, len(sub_g.nodes)))
        return sub_g


if __name__ == '__main__':
    graph_dao = GraphDAO('../../dataset/graph.db', use_cache=True)
    print(1)
