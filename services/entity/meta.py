import gc
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
                target_id, edge_id = random.choice(_edges)  # 随机游走
                # all_edges.append({'source_id': node_id, 'target_id': target_id, 'edge_id': edge_id})
                all_edges.append((node_id, edge_id, target_id))
                all_edges += meta_node.match(target_id)
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

    def match(self, node_id):
        return self.start_node.match(node_id)


global_nodes = dict()


def build_meta_nodes(node_):
    NodeLabels = common.NodeLabels
    EdgeLabels = common.EdgeLabels

    for node_label, next_nodes in node_.items():
        meta_node = MetaNode(NodeLabels[node_label])
        for next_node in next_nodes:
            for _edge, _node in next_node.items():
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
    # 先定义一些公共的点
    for _key, _item in rules['global_nodes'].items():
        global_nodes[_key] = build_meta_nodes(_item)
    meta_paths = list()
    for _key, _item in rules['paths'].items():
        meta_paths.append(MetaPath(_key, build_meta_nodes(_item)))
    return meta_paths
