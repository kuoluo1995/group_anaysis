import json
import queue
import timeit

import networkx as nx
from collections import defaultdict

from services.dao.base_dao import SqliteDAO


class GraphDAO(SqliteDAO):
    def __init__(self, path, use_cache=True):
        super().__init__(path, use_cache)
        self.node_id2code_cache = {}
        self.node_id2name_cache = {}
        self.node_id2en_name_cache = {}
        self.node_id2label_cache = {}
        self.node_label_code2id_cache = defaultdict(dict)
        self.edge_id2label_cache = {}
        self.edge_id2name_cache = {}
        self.edge_id2en_name_cache = {}
        self.in_edge_cache = {}
        self.out_edge_cache = {}
        self.address_id2person_ids_cache = {}
        self.node_id2has_topic_person_cache = {}
        self.post_type_id2person_ids_cache = {}
        self.post_address_id2person_ids_cache = {}
        self.office_id2person_ids_cache = {}
        self.office_type_id2person_ids_cache = {}
        self.entry_id2person_ids_cache = {}
        self.entry_type_id2person_ids_cache = {}
        # if self.use_cache:  # todo 如果电脑性能允许的话，为了加快运行速度可以考虑提前载入数据
        #     self.start_connect()
        #     self.__import_all_data()
        #     self.close_connect()

    def __import_all_data(self):
        sql_str = '''SELECT DISTINCT id, name, code, label, en_name FROM node2data'''
        rows = self._select(sql_str, ['id', 'name', 'code', 'label', 'en_name'], ())
        for cols in rows:
            self.node_id2label_cache[int(cols['id'])] = str(cols['label'])
            self.node_id2name_cache[int(cols['id'])] = str(cols['name'])
            self.node_id2en_name_cache[int(cols['id'])] = self.format_en_name(str(cols['en_name']))
        sql_str = '''SELECT id, label, name, en_name FROM rel2data'''
        rows = self._select(sql_str, ['id', 'label', 'name', 'en_name'], ())
        for cols in rows:
            self.edge_id2label_cache[int(cols['id'])] = str(cols['label'])
            self.edge_id2name_cache[int(cols['id'])] = str(cols['name'])
            self.edge_id2en_name_cache[int(cols['id'])] = self.format_en_name(str(cols['en_name']))

    def get_all_post_types(self):
        sql_str = '''SELECT DISTINCT post_type_id FROM post_type2person_ids'''
        rows = self._select(sql_str, ['post_type_id'], ())
        return [int(cols['post_type_id']) for cols in rows]

    def get_all_post_address(self):
        sql_str = '''SELECT DISTINCT post_address_id FROM post_address2person_ids'''
        rows = self._select(sql_str, ['post_address_id'], ())
        return [int(cols['post_address_id']) for cols in rows]

    def get_all_offices(self):
        sql_str = '''SELECT DISTINCT office_id FROM office2person_ids'''
        rows = self._select(sql_str, ['office_id'], ())
        return [int(cols['office_id']) for cols in rows]

    def get_all_office_types(self):
        sql_str = '''SELECT DISTINCT office_type_id FROM office_type2person_ids'''
        rows = self._select(sql_str, ['office_type_id'], ())
        return [int(cols['office_type_id']) for cols in rows]

    def get_all_entries(self):
        sql_str = '''SELECT DISTINCT entry_id FROM entry2person_ids'''
        rows = self._select(sql_str, ['entry_id'], ())
        return [int(cols['entry_id']) for cols in rows]

    def get_all_entry_types(self):
        sql_str = '''SELECT DISTINCT entry_type_id FROM entry_type2person_ids'''
        rows = self._select(sql_str, ['entry_type_id'], ())
        return [int(cols['entry_type_id']) for cols in rows]

    def get_all_address(self):
        sql_str = '''SELECT DISTINCT address_id FROM address2person_ids'''
        rows = self._select(sql_str, ['address_id'], ())
        return [int(cols['address_id']) for cols in rows]

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
                self.node_id2en_name_cache[int(cols['id'])] = self.format_en_name(str(cols['en_name']))
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
            self.node_id2en_name_cache[node_id] = self.format_en_name(str(rows[0]['en_name']))
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
            self.node_id2en_name_cache[node_id] = self.format_en_name(str(rows[0]['en_name']))
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
            self.node_id2en_name_cache[node_id] = self.format_en_name(str(rows[0]['en_name']))
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
            self.node_id2en_name_cache[node_id] = self.format_en_name(str(rows[0]['en_name']))
        return self.node_id2label_cache[node_id]

    def get_node_ids_by_name(self, node_name, node_label='Person'):  # 非年份的所有结点
        sql_str = '''SELECT id FROM node2data WHERE name = ? and label = ?'''
        rows = self._select(sql_str, ['id'], (node_name, node_label,))
        if len(rows) == 0:
            sql_str = '''SELECT id FROM node2data WHERE en_name = ? and label = ?'''
            rows = self._select(sql_str, ['id'], (node_name, node_label,))
        return [int(cols['id']) for cols in rows]

    def get_node_ids_by_label(self, node_label):
        sql_str = '''SELECT id FROM node2data WHERE label = ?'''
        rows = self._select(sql_str, ['id'], (node_label,))
        return [int(cols['id']) for cols in rows]

    # siwei: 找到描述中包含节点的人(必须是总描述数量超过10个的人)
    def get_person_ids_by_node_id(self, node_id):
        if node_id not in self.node_id2has_topic_person_cache:
            sql_str = '''SELECT person_id2count FROM node2person2count WHERE node_id = ?'''
            rows = self._select(sql_str, ['person_id2count'], (node_id,))
            if len(rows) == 0:
                print(node_id, self.get_node_name_by_id(node_id), '没有对应的person_id2count')
                person_ids = set()
            else:
                person_ids = json.loads(rows[0]['person_id2count']).keys()
                person_ids = set([int(_id) for _id in person_ids])
            if not self.use_cache:
                return person_ids
            self.node_id2has_topic_person_cache[node_id] = person_ids
        return self.node_id2has_topic_person_cache[node_id]

    def get_person_ids_by_address_id(self, address_id):
        if address_id not in self.address_id2person_ids_cache:
            sql_str = '''SELECT person_ids FROM address2person_ids WHERE address_id = ?'''
            rows = self._select(sql_str, ['person_ids'], (address_id,))
            if len(rows) == 0:
                print(address_id, self.get_node_name_by_id(address_id), '没有对应的person_id')
                person_ids = set()
            else:
                person_ids = json.loads(rows[0]['person_ids'])
                person_ids = set([int(_id) for _id in person_ids])
            if not self.use_cache:
                return person_ids
            self.address_id2person_ids_cache[address_id] = person_ids
        return self.address_id2person_ids_cache[address_id]

    def get_person_ids_by_post_type_id(self, post_type_id):
        if post_type_id not in self.post_type_id2person_ids_cache:
            sql_str = '''SELECT person_ids FROM post_type2person_ids WHERE post_type_id = ?'''
            rows = self._select(sql_str, ['person_ids'], (post_type_id,))
            if len(rows) == 0:
                print(post_type_id, self.get_node_name_by_id(post_type_id), '没有对应的person_id')
                person_ids = set()
            else:
                person_ids = json.loads(rows[0]['person_ids'])
                person_ids = set([int(_id) for _id in person_ids])
            if not self.use_cache:
                return person_ids
            self.post_type_id2person_ids_cache[post_type_id] = person_ids
        return self.post_type_id2person_ids_cache[post_type_id]

    def get_person_ids_by_post_address_id(self, post_address_id):
        if post_address_id not in self.post_address_id2person_ids_cache:
            sql_str = '''SELECT person_ids FROM post_address2person_ids WHERE post_address_id = ?'''
            rows = self._select(sql_str, ['person_ids'], (post_address_id,))
            if len(rows) == 0:
                print(post_address_id, self.get_node_name_by_id(post_address_id), '没有对应的person_id')
                person_ids = set()
            else:
                person_ids = json.loads(rows[0]['person_ids'])
                person_ids = set([int(_id) for _id in person_ids])
            if not self.use_cache:
                return person_ids
            self.post_address_id2person_ids_cache[post_address_id] = person_ids
        return self.post_address_id2person_ids_cache[post_address_id]

    def get_person_ids_by_office_id(self, office_id):
        if office_id not in self.office_id2person_ids_cache:
            sql_str = '''SELECT person_ids FROM office2person_ids WHERE office_id = ?'''
            rows = self._select(sql_str, ['person_ids'], (office_id,))
            if len(rows) == 0:
                print(office_id, self.get_node_name_by_id(office_id), '没有对应的person_id')
                person_ids = set()
            else:
                person_ids = json.loads(rows[0]['person_ids'])
                person_ids = set([int(_id) for _id in person_ids])
            if not self.use_cache:
                return person_ids
            self.office_id2person_ids_cache[office_id] = person_ids
        return self.office_id2person_ids_cache[office_id]

    def get_person_ids_by_office_type_id(self, office_type_id):
        if office_type_id not in self.office_type_id2person_ids_cache:
            sql_str = '''SELECT person_ids FROM office_type2person_ids WHERE office_type_id = ?'''
            rows = self._select(sql_str, ['person_ids'], (office_type_id,))
            if len(rows) == 0:
                print(office_type_id, self.get_node_name_by_id(office_type_id), '没有对应的person_id')
                person_ids = set()
            else:
                person_ids = json.loads(rows[0]['person_ids'])
                person_ids = set([int(_id) for _id in person_ids])
            if not self.use_cache:
                return person_ids
            self.office_type_id2person_ids_cache[office_type_id] = person_ids
        return self.office_type_id2person_ids_cache[office_type_id]

    def get_person_ids_by_entry_id(self, entry_id):
        if entry_id not in self.entry_id2person_ids_cache:
            sql_str = '''SELECT person_ids FROM entry2person_ids WHERE entry_id = ?'''
            rows = self._select(sql_str, ['person_ids'], (entry_id,))
            if len(rows) == 0:
                print(entry_id, self.get_node_name_by_id(entry_id), '没有对应的person_id')
                person_ids = set()
            else:
                person_ids = json.loads(rows[0]['person_ids'])
                person_ids = set([int(_id) for _id in person_ids])
            if not self.use_cache:
                return person_ids
            self.entry_id2person_ids_cache[entry_id] = person_ids
        return self.entry_id2person_ids_cache[entry_id]

    def get_person_ids_by_entry_type_id(self, entry_type_id):
        if entry_type_id not in self.entry_type_id2person_ids_cache:
            sql_str = '''SELECT person_ids FROM entry_type2person_ids WHERE entry_type_id = ?'''
            rows = self._select(sql_str, ['person_ids'], (entry_type_id,))
            if len(rows) == 0:
                print(entry_type_id, self.get_node_name_by_id(entry_type_id), '没有对应的person_id')
                person_ids = set()
            else:
                person_ids = json.loads(rows[0]['person_ids'])
                person_ids = set([int(_id) for _id in person_ids])
            if not self.use_cache:
                return person_ids
            self.entry_type_id2person_ids_cache[entry_type_id] = person_ids
        return self.entry_type_id2person_ids_cache[entry_type_id]

    def get_edge_label_by_id(self, edge_id):
        if edge_id == -1:
            return 'End'
        if edge_id not in self.edge_id2label_cache:
            sql_str = '''SELECT label, name, en_name FROM rel2data WHERE id = ?'''
            rows = self._select(sql_str, ['label', 'name', 'en_name'], (edge_id,))
            if not self.use_cache:
                return str(rows[0]['label'])
            self.edge_id2label_cache[edge_id] = str(rows[0]['label'])
            self.edge_id2name_cache[edge_id] = str(rows[0]['name'])
            self.edge_id2en_name_cache[edge_id] = self.format_en_name(str(rows[0]['en_name']))
        return self.edge_id2label_cache[edge_id]

    def get_edge_name_by_id(self, edge_id):
        if edge_id == -1:
            return '；'
        if edge_id not in self.edge_id2name_cache:
            sql_str = '''SELECT label, name, en_name FROM rel2data WHERE id = ?'''
            rows = self._select(sql_str, ['label', 'name', 'en_name'], (edge_id,))
            if not self.use_cache:
                return str(rows[0]['name'])
            self.edge_id2label_cache[edge_id] = str(rows[0]['label'])
            self.edge_id2name_cache[edge_id] = str(rows[0]['name'])
            self.edge_id2en_name_cache[edge_id] = self.format_en_name(str(rows[0]['en_name']))
        return self.edge_id2name_cache[edge_id]

    def get_edge_en_name_by_id(self, edge_id):
        if edge_id == -1:
            return ';'
        if edge_id not in self.edge_id2en_name_cache:
            sql_str = '''SELECT label, name, en_name FROM rel2data WHERE id = ?'''
            rows = self._select(sql_str, ['label', 'name', 'en_name'], (edge_id,))
            if not self.use_cache:
                return str(rows[0]['en_name'])
            self.edge_id2label_cache[edge_id] = str(rows[0]['label'])
            self.edge_id2name_cache[edge_id] = str(rows[0]['name'])
            self.edge_id2en_name_cache[edge_id] = self.format_en_name(str(rows[0]['en_name']))
        return self.edge_id2en_name_cache[edge_id]

    def get_in_edges(self, target_id):
        if target_id not in self.in_edge_cache:
            rows = self._select('''SELECT source, r_id FROM graph WHERE target = ?''', ['source', 'r_id'], (target_id,))
            rows = [(int(row['source']), target_id, int(row['r_id'])) for row in rows]  # 减小内存消耗
            if not self.use_cache:
                return rows
            self.in_edge_cache[target_id] = rows
        return self.in_edge_cache[target_id]

    def get_out_edges(self, source_id):
        if source_id not in self.out_edge_cache:
            rows = self._select('''SELECT target, r_id FROM graph WHERE source = ?''', ['target', 'r_id'], (source_id,))
            rows = [(source_id, int(row['target']), int(row['r_id'])) for row in rows]
            if not self.use_cache:
                return rows
            self.out_edge_cache[source_id] = rows
        return self.out_edge_cache[source_id]

    def get_sub_graph(self, node_id, max_depth=3):  # 我的实现方式慢一些，可能由于Queue这里线程安全的缘故？
        start = timeit.default_timer()
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

    def format_en_name(self, _en_name):
        if '(' in _en_name:
            _i = _en_name.index('(')
            if _en_name[_i - 1] != ' ':
                _en_name = _en_name[:_i] + ' ' + _en_name[_i:]
        return _en_name


if __name__ == '__main__':
    graph_dao = GraphDAO('../../dataset/graph.db', use_cache=True)
    print(1)
