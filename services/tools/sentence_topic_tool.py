import math
import random
import numpy as np
from collections import defaultdict

from services import common
from services.tools.graph_tool import graph_id2string, get_filtered_node
from tools.analysis_utils import multidimensional_scale
from tools.sort_utils import sort_dict2list, maxN

"""
Sentence 部分
========
    下面是关于Sentence的所有函数
"""


def get_sentence_ids_dict(person_ids, random_epoch=100):
    """根据人的id 随机游走找到响应的描述

    Parameters
    ----------
    person_ids: list(int)
        所有相关人的id
    random_epoch: int
        随机游走的迭代步数

    Returns
    -------
    person_id2sentence_ids: dict{int: list(int)}
        人的id对应到描述的id
    sentence_id2person_id: dict{list(int): int}
        描述的id（node_id,edge_id,node_id。。。）作为key,每个描述对应着每个人的id
    all_sentence_ids: list(list(int))
        所有的描述，以及描述里所有的id（node_id,edge_id,node_id。。。）
    """
    MetaPaths = common.MetaPaths

    person_id2sentence_ids = {}  # 描述
    sentence_id2person_id = {}
    all_sentence_ids = set()
    for person_id in person_ids:
        sentence_ids = set()
        for i in range(random_epoch):
            meta_path = random.choice(MetaPaths)
            _ids = meta_path.match(person_id)
            if len(_ids) > 0:
                sentence_id = []
                for _source_id, _edge_id, _target_id in _ids:
                    sentence_id += [_source_id, _edge_id, _target_id]
                sentence_id = tuple(sentence_id)  # list没法hash，所以要转化成元组
                sentence_ids.add(sentence_id)
                sentence_id2person_id[sentence_id] = person_id
                all_sentence_ids.add(sentence_id)
        person_id2sentence_ids[person_id] = sentence_ids
    return person_id2sentence_ids, sentence_id2person_id, all_sentence_ids


def get_sentence_id2relevancy(sentence_id_, node_id2relevancy):
    """计算描述的相似度

    Parameters
    ----------
    sentence_id_: list(int)
        所有描述的id (node_id, edge_id, node_id) 描述由三元元组组成。所以i%3=0和i%3=2都是node, i%3=1是edge
    node_id2relevancy: dict{int: float}
        这是个字典，用来算描述的相似度

    Returns
    -------
    :float
        相似度的值
    """
    sentence_id2relevancy = 0
    for i, _id in enumerate(sentence_id_):
        if i % 3 == 0 or i % 3 == 2:
            sentence_id2relevancy += node_id2relevancy[_id]
    return sentence_id2relevancy / len(sentence_id_) * 1.5  # 排除掉边， node edge node


def get_sentence_id2vector(all_sentence_ids):
    """计算描述的相似度

    Parameters
    ----------
    all_sentence_ids: list(list(int))
        所有的描述的id

    Returns
    -------
    _sentence_id2vector: dict{list(int): array}
        根据描述得到相似度字典
    """
    model = common.Model

    _sentence_id2vector = {}
    for _sentence_id in all_sentence_ids:
        _sentence = graph_id2string(_sentence_id)
        _sentence_id2vector[_sentence_id] = model.infer_vector(_sentence)
    return _sentence_id2vector


"""
Topic
========
    下面是关于Topic的所有函数
"""


# 多少能算显著特性
def get_topic_id_dict(node_label2ids, relevancy_dict, all_sentence_ids, sentence_id2relevancy, sentence_id2person_id,
                      len_person, max_topic=15, populate_ratio=0.3):
    """根据相关的人和描述，得到所有有关的topic， topic其实就是node_name

    Parameters
    ----------
    node_label2ids: dict{string: list(int)}
        每个label里包含的所有id
    relevancy_dict: dict{int: float}
        节点相似度的字典 dict{node_id:相似度}
    all_sentence_ids: list(list(int))
        所有的描述，描述是(node_id,edge_id,node_id。。。。)组成
    sentence_id2relevancy: dict{list(int): float}
        描述的id以及其对应的相似度
    sentence_id2person_id: dict{list(int):int}
        描述的id及其对应的person_id
    len_person: int
        所有相关人的人数
    max_topic: int
        最多多少个topic
    populate_ratio: float
        筛选的比例，topic占人口比例多少才算populate topic

    Returns
    -------
    label2topic_ids: dict{string: list(int)}
        label下所包含的全部topic_name的id
    topic_id2sentence_ids: dict{int: list(int)}
        topic_id对应的所有描述，以及描述是由list组成的。里面是(node_id,edge_id,node_id。。。。)组成
    all_topic_ids: list(int)
        topic其实就是name, 所以就是node_name对应的id集合
    """
    label2topic_ids, topic_id2sentence_ids, all_topic_ids = {}, {}, list()
    for _label, _ids in node_label2ids.items():
        _node_id2relevancy = dict()  # node_id2relevancy是个计算当前结点里已有结点的相关性
        for _id in _ids:
            _node_id2relevancy[_id] = relevancy_dict[_id]
        _node_id2relevancy = sort_dict2list(_node_id2relevancy)
        popular_node_ids = []
        for (_node_id, _) in _node_id2relevancy:
            is_need, _id = get_filtered_node(_node_id)
            if is_need:
                popular_node_ids.append(_id)
        popular_node_ids = np.array(popular_node_ids)[:max_topic]
        topic_ids = list()
        for _node_id in popular_node_ids:
            sentence_ids = [_sentence_id for _sentence_id in all_sentence_ids if _node_id in _sentence_id]
            sentence_ids = maxN(sentence_ids, key=lambda item: sentence_id2relevancy[item])
            person_ids = set([sentence_id2person_id[_sentence_id] for _sentence_id in sentence_ids])
            if len(person_ids) > len_person * populate_ratio:  # 剃掉那些不算不上群体的
                topic_ids.append(_node_id)
                topic_id2sentence_ids[_node_id] = sentence_ids  # 小圆点
        label2topic_ids[_label] = topic_ids
        all_topic_ids += topic_ids
    return label2topic_ids, topic_id2sentence_ids, all_topic_ids


def get_topic_pmi(all_topic_ids, person_id2sentence_ids, topic_id2sentence_ids, all_sentence_ids):
    """计算所有topic的pmi 标签之间的相关性，每个Topic的连线，越高先关系越大 pmi点互信息（概率论）

    Parameters
    ----------
    all_topic_ids: list(int)
        topic其实就是name, 所以就是node_name对应的id集合
    person_id2sentence_ids: dict{int: list(int)}
        人的id对应到描述的id
    topic_id2sentence_ids: dict{int: list(int)}
        topic_id对应的所有描述，以及描述是由list组成的。里面是(node_id,edge_id,node_id。。。。)组成
    all_sentence_ids: list(list(int))
        所有的描述，描述是(node_id,edge_id,node_id。。。。)组成

    Returns
    -------
    pmi_node: dict{int: dict{int: float}}
        topic的pmi矩阵 标签之间的相关性，每个Topic的连线，越高先关系越大 pmi点互信息（概率论）
    """
    # 统计topic
    count_x, count_xy = defaultdict(int), defaultdict(dict)
    for _x in all_topic_ids:
        count_xy[_x] = defaultdict(int)
        for _sentence_ids in person_id2sentence_ids.values():
            for _sentence_id in _sentence_ids:
                if _sentence_id in topic_id2sentence_ids[_x]:  # 每一个topic对于所有的描述
                    count_x[_x] += 1
                    break
        for _y in all_topic_ids:
            for _sentence_ids in person_id2sentence_ids.values():
                has_x = has_y = False
                for _sentence_id in _sentence_ids:
                    if _sentence_id in topic_id2sentence_ids[_x]:
                        has_x = True
                    if _sentence_id in topic_id2sentence_ids[_y]:
                        has_y = True
                if has_x and has_y:
                    count_xy[_x][_y] += 1
    # 计算pmi
    pmi_node = {}
    for _x in all_topic_ids:
        pmi_node[_x] = defaultdict(int)
        for _y in all_topic_ids:
            if count_x[_x] == 0 or count_x[_y] == 0:
                pmi_node[_x][_y] = 0
                continue
            p_xy = count_xy[_x][_y] / count_x[_y]  # p(x|y)
            p_x = count_x[_x] / len(all_sentence_ids)  # p(x)
            pmi = p_xy / p_x
            pmi_node[_x][_y] = 0 if pmi == 0 or _x == _y else math.log(pmi)
    return pmi_node


def get_sentence_id2position1d(sentence_ids, sentence_id2vector):
    """计算所有描述里的相似度位置

    Parameters
    ----------
    sentence_ids: list(list(int))
        所有描述，以及描述是由list组成的。里面是(node_id,edge_id,node_id。。。。)组成
    sentence_id2vector: dict{list(int):array}
        所有的描述，描述是(node_id,edge_id,node_id。。。。)组成

    Returns
    -------
    sentence_id2position1d: dict{list(int): float}
        描述id所对应的一维位置
    """
    _vectors = np.array([sentence_id2vector[_sentence_id] for _sentence_id in sentence_ids])
    positions = multidimensional_scale(1, data=_vectors)  # 一维展示数组
    sentence_id2position1d = dict()
    for i, _pos1d in enumerate(positions):
        sentence_id = sentence_ids[i]
        value = _pos1d[0]  # 一维
        sentence_id2position1d[sentence_id] = value
    return sentence_id2position1d
