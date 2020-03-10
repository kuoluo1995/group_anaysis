import math
import timeit
import networkx as nx
from collections import defaultdict

from services import common


def get_node_relevancy(person_ids):
    """计算所有人的节点的相关度
    Notes
    ----------
    这里的范围是通过图数据库的内容查询的

    Parameters
    ----------
    person_ids: list(int)

    Returns
    -------
    node_label2ids: dict{string: list(int)}
        同一个label里所有的id。为后期找topic做准备，id可以对应到topic的name
    node_id2relevancy: dict{int: float}
        节点对应的先相关度用于
    """
    GRAPH_DAO = common.GRAPH_DAO
    person_graph = {_id: GRAPH_DAO.getSubGraph(_id, depth=3) for _id in person_ids}
    # person_graph = {_id: GRAPH_DAO.get_sub_graph(_id, max_depth=3) for _id in person_ids}
    person_graph_tree = {person_id: nx.bfs_tree(sub_graph, person_id) for person_id, sub_graph in person_graph.items()}

    # 得到所有相关结点, NodeView没法直接hashable，所以加了list
    all_related_node_ids = []
    for _, _graph in person_graph.items():
        all_related_node_ids += _graph.nodes()
    all_related_node_ids = set(all_related_node_ids)

    node_label2ids = defaultdict(list)  # 为后期加快计算做准备
    node_id2relevancy = defaultdict(int)  # 相关度集合
    for _id in all_related_node_ids:
        # name_ = GRAPH_DAO.get_node_name_by_id(_id)
        is_need, _id = get_filtered_node(_id)
        if is_need:  # 检测是否被过滤掉了？
            # 计算结点的相关值
            count_yx = 0  # count(y,x)
            relevancy_yx = 0  # 相关度值
            for _person_id, _sub_graph in person_graph.items():
                _sub_graph_tree = person_graph_tree[_person_id]
                if _id in _sub_graph:
                    count_yx += 1
                    depth = nx.shortest_path_length(_sub_graph_tree, _person_id, _id)
                    relevancy_yx += 1 / math.log(depth + 2)
            node_label = GRAPH_DAO.get_node_label_by_id(_id)
            node_label2ids[node_label].append(_id)
            node_id2relevancy[_id] += relevancy_yx  # todo
    return node_label2ids, node_id2relevancy


# def get_node_relevancy(person_ids):
#     """计算所有人的节点的相关度
#     Notes
#     ----------
#     这里的范围是通过图数据库的内容查询的
#
#     Parameters
#     ----------
#     person_ids: list(int)
#
#     Returns
#     -------
#     node_label2ids: dict{string: list(int)}
#         同一个label里所有的id。为后期找topic做准备，id可以对应到topic的name
#     node_id2relevancy: dict{int: float}
#         节点对应的先相关度用于
#     """
#     GRAPH_DAO = common.GRAPH_DAO
#
#     _start = timeit.default_timer()
#     # person_graph = {_id: GRAPH_DAO.get_sub_graph(_id, max_depth=2) for _id in person_ids}
#     person_graph = {_id: GRAPH_DAO.getSubGraph(_id, depth=3) for _id in person_ids}
#     person_graph_tree = {person_id: nx.bfs_tree(sub_graph, person_id) for person_id, sub_graph in person_graph.items()}
#     print('node_relevancy:{}'.format(timeit.default_timer() - _start))
#
#     # 得到所有相关结点, NodeView没法直接hashable，所以加了list
#     all_related_node_ids = []
#     for _, _graph in person_graph.items():
#         all_related_node_ids += _graph.nodes()
#     all_related_node_ids = set(all_related_node_ids)
#
#     node_label2ids = defaultdict(list)  # 为后期加快计算做准备
#     node_id2relevancy = defaultdict(int)  # 相关度集合
#     for _id in all_related_node_ids:
#         name_ = GRAPH_DAO.get_node_name_by_id(_id)
#         # is_need, _id = get_filtered_node(_id)
#         if name_ != 'None':  # 检测是否被过滤掉了？
#             # 计算结点的相关值
#             count_yx = 0  # count(y,x)
#             relevancy_yx = 0  # 相关度值
#             for _person_id, _sub_graph in person_graph.items():
#                 _sub_graph_tree = person_graph_tree[_person_id]
#                 if _id in _sub_graph:
#                     count_yx += 1
#                     depth = nx.shortest_path_length(_sub_graph_tree, _person_id, _id)
#                     relevancy_yx += 1 / math.log(depth + 2)
#             node_label = GRAPH_DAO.get_node_label_by_id(_id)
#             node_label2ids[node_label].append(_id)
#             node_id2relevancy[_id] = relevancy_yx  # todo node_id2relevancy[_id] += relevancy_yx
#     return node_label2ids, node_id2relevancy


def graph_id2string(graph_ids):
    """将描述id转换成语言 graph_id = node_id edge_id node_id
    Notes
    ----------
    这里的范围是通过图数据库的内容查询的

    Parameters
    ----------
    graph_ids: list(int)

    Returns
    -------
    sentence: list(string)
    """
    GRAPH_DAO = common.GRAPH_DAO
    sentence = list()
    for i, id_ in enumerate(graph_ids):
        if i % 3 == 0 or i % 3 == 2:
            sentence.append(GRAPH_DAO.get_node_name_by_id(id_))
        else:
            sentence.append(GRAPH_DAO.get_edge_name_by_id(id_))
    return sentence


def get_filtered_node(id_=None, name_=None, label_=None):
    """筛选结点,进行加快计算
    Notes
    ----------
    这里的范围是通过图数据库的内容查询的

    Parameters
    ----------
    id_: int or None
        根据id来筛选节点
    name_: string or None
        根据name来筛选节点
    label_: string or None
        根据label来筛选节点
    Returns
    -------
    : bool
        是否需要？需要这个节点就是Yes, 被筛选掉就是None
    id: int or None
        如果这个节点需要就返回id_，如果不需要就返回None

    """
    GRAPH_DAO = common.GRAPH_DAO
    NodeLabels = common.NodeLabels

    if id_ is not None and name_ is None:
        name_ = GRAPH_DAO.get_node_name_by_id(id_)
    if name_ in ['None', '0', '未详', '[未详]']:
        return False, None
    # if id_ is not None and label_ is None:
    #     label_ = GRAPH_DAO.get_node_label_by_id(id_)
    # if label_ in [NodeLabels['post_type'], NodeLabels['address_type']]:  # 这几个label做topic没意义
    #     return False, None
    return True, id_


def get_graph_dict(all_graph_ids):
    """根据图id来得到图的字典，包括节点字典和边字典，为前端这里可以实现多语言化
    Notes
    ----------
    这里的范围是通过图数据库的内容查询的

    Parameters
    ----------
    all_graph_ids: list(list())
        all_graph_ids代表着所有的描述的id, 然后里面的每个item代表一句描述，描述是由三元数组组成的。
        node_id, edge_id, node_id 将这些所有的三元数组组合成列表。

    Returns
    -------
    node_dict: dict{int:dict{string: string}}
        节点字典： {node_id: {'name': name, 'label':label, 'en_name': en_name}}
    edge_dict: dict{int:dict{string: string}}
        边字典: {edge_id: {'name': name, 'label': label, 'en_name': en_name}}

    """
    GRAPH_DAO = common.GRAPH_DAO

    node_dict = {}
    edge_dict = {}
    for graph_id in all_graph_ids:
        for i, _id in enumerate(graph_id):
            if i % 3 == 0 or i % 3 == 2:
                node_dict[_id] = {'name': GRAPH_DAO.get_node_name_by_id(_id),
                                  'label': GRAPH_DAO.get_node_label_by_id(_id),
                                  'en_name': GRAPH_DAO.get_node_en_name_by_id(_id)}
            else:
                edge_dict[_id] = {'name': GRAPH_DAO.get_edge_name_by_id(_id),
                                  'label': GRAPH_DAO.get_edge_label_by_id(_id),
                                  'en_name': GRAPH_DAO.get_edge_en_name_by_id(_id)}
    return node_dict, edge_dict
