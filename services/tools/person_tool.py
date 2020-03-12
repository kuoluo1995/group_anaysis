from collections import defaultdict

import math
import numpy as np

from tools.analysis_utils import multidimensional_scale
from tools.sort_utils import mean_vectors, cos_dict


def get_person_id2position2d(sentence_id2vector, person_id2sentence_ids, **kwargs):
    """根据人的id查询所有的地址及坐标
    Notes
    ----------
    这里是通过CBDB数据库的内容查询的,但是整个函数传出来的id全是以图数据库为准

    Parameters
    ----------
    sentence_id2vector: list(int)
        所有相关人的id
    person_id2sentence_ids: int
        随机游走的迭代步数
    **kwargs: dict
        里面可能包含:
        topic_id2sentence_ids_: dict{int: list(list(int))
            结点的id: list(描述) 描述里面是所有的id， 按照node_id, edge_id, node_id划分
        num_dim:
            num_dim 代表模型的维度
    Returns
    -------
    person_id2position2d: dict{int: (int, int)}
        { person_id: (x,y)}
    """
    return get_person_id2position2d_1(sentence_id2vector, person_id2sentence_ids, **kwargs)  # 学长的方案
    # return get_person_id2position2d_2(sentence_id2vector, person_id2sentence_ids, **kwargs) # 我的方案


# 计算人物相似度方案一(学长)
def get_person_id2position2d_1(sentence_id2vector, person_id2sentence_ids, topic_id2sentence_ids_, num_dim, **kwargs):
    num_topic = len(topic_id2sentence_ids_.keys())
    person_id2vector = {person_id: np.zeros(num_topic * num_dim) for person_id in person_id2sentence_ids.keys()}
    _i = 0
    for _topic_id, _sentence_ids in topic_id2sentence_ids_.items():
        _topic_vectors = np.array([sentence_id2vector[_sentence_id] for _sentence_id in _sentence_ids])
        _mean = mean_vectors(_topic_vectors)
        for person_id in person_id2sentence_ids.keys():
            max_vector = _mean
            _vectors = [sentence_id2vector[_sentence_id] for _sentence_id in person_id2sentence_ids[person_id] if
                        _sentence_id in _sentence_ids]
            if len(_vectors) > 0:
                max_vector = max(_vectors, key=lambda item: cos_dict(item, _mean))
            # 可以在这里加个维度的权重参数
            person_id2vector[person_id][_i * num_dim:(_i + 1) * num_dim] = max_vector
        _i += 1
    _vectors = np.array([_vector for _, _vector in person_id2vector.items()])
    positions = multidimensional_scale(2, data=_vectors)

    _i = 0
    person_id2position2d = dict()
    for _person_id, _ in person_id2vector.items():
        person_id2position2d[_person_id] = (positions[_i][0], positions[_i][1])  # x,y
        _i += 1
    return person_id2position2d


# 计算人物相似度方案二
def get_person_id2position2d_2(sentence_id2vector, person_id2sentence_ids, **kwargs):
    # 直接统计每个人的相似度平局值来计算其相似度
    _vectors = list()
    for _, _sentence_ids in person_id2sentence_ids.items():
        person_vectors = np.array([sentence_id2vector[_sentence_id] for _sentence_id in _sentence_ids])
        _mean = mean_vectors(person_vectors)
        _vectors.append(_mean)
    positions = multidimensional_scale(2, data=np.array(_vectors))

    _i = 0
    person_id2positions2d = dict()
    for _person_id, _ in person_id2sentence_ids.items():
        person_id2positions2d[_person_id] = (positions[_i][0], positions[_i][1])
        _i += 1
    return person_id2positions2d


def get_person_pmi(all_person_ids, person_id2sentence_ids, num_all_sentences):
    """计算所有person的pmi

    Parameters
    ----------
    all_person_ids: list(int)
        topic其实就是name, 所以就是node_name对应的id集合
    person_id2sentence_ids: dict{int: list(int)}
        人的id对应到描述的id
    num_all_sentences: int
        所有的描述数量

    Returns
    -------
    pmi_node: dict{int: dict{int: float}}
        person的pmi矩阵 标签之间的相关性，越高先关系越大 pmi点互信息（概率论）
    """
    # 统计person
    count_x, count_xy = dict(), defaultdict(dict)
    for _x in all_person_ids:
        count_x[_x] = len(person_id2sentence_ids[_x])
        count_xy[_x] = defaultdict(int)
        for _y in all_person_ids:
            for _sentence_id in person_id2sentence_ids[_x]:
                if _y in _sentence_id:
                    count_xy[_x][_y] += 1
    # 计算pmi
    pmi_node = {}
    for _x in all_person_ids:
        pmi_node[_x] = defaultdict(int)
        for _y in all_person_ids:
            if count_x[_x] == 0 or count_x[_y] == 0:
                pmi_node[_x][_y] = 0
                continue
            p_xy = count_xy[_x][_y] / count_x[_y]  # p(x|y)
            p_x = count_x[_x] / num_all_sentences  # p(x)
            pmi = p_xy / p_x
            pmi_node[_x][_y] = 0 if pmi == 0 or _x == _y else math.log(pmi)
    return pmi_node
