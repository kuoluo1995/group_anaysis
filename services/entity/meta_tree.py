import random

from services import common
from tools import yaml_utils


class MetaNode:
    def __init__(self, label):
        self.label = label
        self.next_nodes = list()

    def match(self, node_id):
        DAO = common.GRAPH_DAO
        all_nodes = {node_id}
        tree = {node_id: []}
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
                for target_id, edge_id in _edges:
                    _sub_tree, _nodes = meta_node.match(target_id)
                    all_nodes.update(_nodes)
                    tree[node_id].append({'edge_id': edge_id, 'target_id': _sub_tree})
        return tree, all_nodes


class MetaPath:
    def __init__(self, name, start_node):
        self.name = name
        self.start_node = start_node
        self.tree = None
        self.used_up = False
        self.node_cache = []

    def build_path_tree(self, node_id):
        self.tree, self.node_cache = self.start_node.match(node_id)
        return self

    def get_edge_id(self, edge_label, target_id):
        GRAPH_DAO = common.GRAPH_DAO
        if target_id in self.node_cache:
            return None

        def _visit_tree(sub_tree, edge_id=None):
            for _node_id, _children in sub_tree.items():
                if (edge_id is not None) or len(_children) == 0:
                    return edge_id
                for _child in _children:
                    _label = GRAPH_DAO.get_edge_label_by_id(_child['edge_id'])
                    if edge_label == _label:
                        edge_id = _child['edge_id']
                    edge_id = _visit_tree(_child['target_id'], edge_id)
                return edge_id

        edge_id = _visit_tree(self.tree)
        return edge_id

    def get_node_id(self, node_label, target_id):
        GRAPH_DAO = common.GRAPH_DAO
        if target_id in self.node_cache:
            return None

        def _visit_tree(sub_tree, node_id=None):
            for _node_id, _children in sub_tree.items():
                if (node_id is not None) or len(_children) == 0:
                    return node_id
                for _child in _children:
                    _label = GRAPH_DAO.get_node_label_by_id(_node_id)
                    if node_label == _label:
                        node_id = _node_id
                    node_id = _visit_tree(_child['target_id'], node_id)
                return node_id

        node_id = _visit_tree(self.tree)
        return node_id

    def get_all_paths(self):
        def _visit_tree(_tree, self=self):
            all_paths = list()
            for _node_id, _children in _tree.items():
                if len(_children) == 0:
                    return [[_node_id, -1]]
                # sub_tree = random.choice(_children)
                for _child in _children:
                    _sub_paths = _visit_tree(_child['target_id'])
                    for _sub_path in _sub_paths:
                        path = list()
                        path.append(_node_id)
                        path.append(_child['edge_id'])
                        path.extend(_sub_path)
                        all_paths.append(path)
                return all_paths

        all_path = _visit_tree(self.tree)
        return all_path

    def random_pop(self):
        if self.used_up or self.tree is None:
            return None

        def _visit_tree(_tree, self=self):
            path = list()
            for _node_id, _children in _tree.items():
                if len(_children) == 0:
                    path.append(_node_id)
                    path.append(-1)  # 句号
                    return path, None

                path.append(_node_id)
                sub_tree = random.choice(_children)
                path.append(sub_tree['edge_id'])
                _sub_path, new_children = _visit_tree(sub_tree['target_id'])
                path.extend(_sub_path)
                if new_children is None:
                    _tree[_node_id].remove(sub_tree)
                    return path, {_node_id: _tree[_node_id]} if len(_tree[_node_id]) > 0 else None
                return path, {_node_id: _tree[_node_id]}

        path, self.tree = _visit_tree(self.tree)
        if self.tree is None:
            self.used_up = True
            return None
        return path


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
    # 先定义一些公共的点
    for _key, _item in rules['global_nodes'].items():
        global_nodes[_key] = build_meta_nodes(_item)
    meta_paths = {}
    for _key, _item in rules['paths'].items():
        meta_paths[_key] = MetaPath(_key, build_meta_nodes(_item))
    return meta_paths
