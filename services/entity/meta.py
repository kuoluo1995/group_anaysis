import random

from services import common
from tools import yaml_utils


class MetaNode:
    def __init__(self, label):
        self.label = label
        self.next_nodes = list()

    def match(self, node_id):
        DAO = common.GRAPH_DAO

        all_edges = []
        node_label = DAO.get_node_label_by_id(node_id)
        if node_label != self.label:
            raise Exception(node_id, node_label, DAO.get_node_name_by_id(node_id), '不符合', self.label)
        for next_node in self.next_nodes:
            for edge_label, meta_node in next_node.items():
                # 可以加个一定几率放弃游走
                _edges = DAO.get_out_edges(node_id)
                _edges = [(_target_id, _edge_id) for _source_id, _target_id, _edge_id in _edges if
                          DAO.get_edge_label_by_id(_edge_id) == edge_label and DAO.get_node_label_by_id(
                              _target_id) == meta_node.label]
                if len(_edges) == 0:
                    continue
                # target_id, edge_id = random.choice(_edges)  # 随机游走
                # all_edges.append((node_id, edge_id, target_id))
                # all_edges += meta_node.match(target_id)
                for _target_id, _edge_id in _edges:
                    sub_edges = meta_node.match(_target_id)
                    if len(sub_edges) == 0:
                        all_edges.append([node_id, _edge_id, _target_id, -1])
                    else:
                        temp = [node_id, _edge_id]
                        for sub_edge in sub_edges:
                            temp.extend(sub_edge)
                        all_edges.append(temp)

        return all_edges

    def __str__(self):
        _str = ' '
        for next_node in self.next_nodes:
            for edge_label, meta_node in next_node.items():
                _str += self.label + '_' + edge_label + '_' + meta_node.label + ':' + str(meta_node) + ';'
        return _str


class MetaPath:
    def __init__(self, name, start_node):
        self.name = name
        self.start_node = start_node
        self.all_paths = None

    def match(self, node_id):
        self.all_paths = self.start_node.match(node_id)
        return self

    def get_all_paths_by_node_id(self, node_id):
        all_paths = self.start_node.match(node_id)
        return all_paths

    def get_node_id_from_paths(self, node_id, node_label):
        if self.all_paths is None:
            return None
        GRAPH_DAO = common.GRAPH_DAO
        for path in self.all_paths:
            if node_id in path and path.index(node_id) % 2 == 0:
                for i, word_id in enumerate(path):
                    if i % 2 == 0:
                        if node_label == GRAPH_DAO.get_node_label_by_id(word_id):
                            return word_id
        return None

    def get_edge_id_from_paths(self, node_id, edge_label):
        if self.all_paths is None:
            return None
        GRAPH_DAO = common.GRAPH_DAO
        for path in self.all_paths:
            if node_id in path and path.index(node_id) % 2 == 0:
                for i, word_id in enumerate(path):
                    if i % 2 == 1:
                        if edge_label == GRAPH_DAO.get_edge_label_by_id(word_id):
                            return word_id
        return None


global_nodes = dict()


def build_meta_nodes(node_):
    NodeLabels = common.NodeLabels
    EdgeLabels = common.EdgeLabels

    for node_label, next_nodes in node_.items():
        meta_node = MetaNode(NodeLabels[node_label])
        for next_node in next_nodes:
            for _edge, _node in next_node.items():
                # print(node_label, _edge, _node)
                if isinstance(_node, dict):
                    meta_node.next_nodes.append({EdgeLabels[_edge]: build_meta_nodes(_node)})
                else:
                    if _node in global_nodes.keys():
                        next_meta_node = global_nodes.get(_node)
                    else:
                        next_meta_node = MetaNode(NodeLabels[_node])
                    meta_node.next_nodes.append({EdgeLabels[_edge]: next_meta_node})
        return meta_node


def build_meta_paths(path):
    rules = yaml_utils.read(path)
    # print(rules)
    # 先定义一些公共的点
    for _key, _item in rules['global_nodes'].items():
        global_nodes[_key] = build_meta_nodes(_item)
    meta_paths = {}
    for _key, _item in rules['paths'].items():
        meta_paths[_key] = MetaPath(_key, build_meta_nodes(_item))
    return meta_paths
