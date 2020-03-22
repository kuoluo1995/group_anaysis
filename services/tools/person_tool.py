import math
import numpy as np
from collections import defaultdict

from services import common
from tools.analysis_utils import multidimensional_scale
from tools.sort_utils import mean_vectors, cos_dict, sort_dict2list


def get_person_ids_by_topic_ids(topic_id1, topic_id2, topic_id2person_ids):
    person_ids = topic_id2person_ids[topic_id1].intersection(topic_id2person_ids[topic_id2])
    return person_ids


def get_person_ids_by_topic_id(topic_id):
    GRAPH_DAO = common.GRAPH_DAO
    person_ids = set()
    for _i, node_id in enumerate(topic_id):
        if _i == 0:
            person_ids = GRAPH_DAO.get_person_ids_by_node_id(node_id)
        else:
            new_person_ids = GRAPH_DAO.get_person_ids_by_node_id(node_id)
            person_ids.intersection_update(new_person_ids)
        if len(person_ids) == 0:
            break
    return person_ids


# 计算人物相似度方案一(学长)
def get_person_id2vector2d(topic_id2sentence_ids2vector, person_id2sentence_ids, num_dim, **kwargs):
    """根据人的id查询所有的地址及坐标

    Notes
    ----------
    这里是通过CBDB数据库的内容查询的,但是整个函数传出来的id全是以图数据库为准

    Parameters
    ----------
    topic_id2sentence_ids2vector: dict{int: list(dict{list(int):array})}
    person_id2sentence_ids: dict{int:list(list(int))}
    num_dim: int
            num_dim 代表模型的维度
    **kwargs: dict
        里面可能包含:
        topic_id2sentence_ids_: dict{int: list(list(int))
            结点的id: list(描述) 描述里面是所有的id， 按照node_id, edge_id, node_id划分

    Returns
    -------
    person_id2position2d: dict{int: (int, int)}
        { person_id: (x,y)}
    """
    num_topic = len(topic_id2sentence_ids2vector.keys())
    person_id2vector = {person_id: np.zeros(num_topic * num_dim) for person_id in person_id2sentence_ids.keys()}
    _i = 0
    for _topic_id, sentence_id2vector in topic_id2sentence_ids2vector.items():
        _topic_vectors = np.array([_vector for _, _vector in sentence_id2vector.items()])
        _mean = mean_vectors(_topic_vectors)
        for person_id in person_id2sentence_ids.keys():
            max_vector = _mean
            _vectors = [sentence_id2vector[_sentence_id] for _sentence_id in person_id2sentence_ids[person_id] if
                        _sentence_id in sentence_id2vector]
            if len(_vectors) > 0:
                max_vector = max(_vectors, key=lambda item: cos_dict(item, _mean))
            # 可以在这里加个维度的权重参数
            person_id2vector[person_id][_i * num_dim:(_i + 1) * num_dim] = max_vector
        _i += 1
    _vectors = np.array([_vector for _, _vector in person_id2vector.items()])
    vectors = multidimensional_scale(2, _vectors)

    _i = 0
    person_id2position2d = dict()
    for _person_id, _ in person_id2vector.items():
        person_id2position2d[_person_id] = (vectors[_i][0], vectors[_i][1])  # x,y
        _i += 1
    return person_id2position2d


def get_all_similar_person(person_ids, topic_id2lrs):
    # siwei: 找到所有相似的人, 要做成一个接口
    # 添加了相似人物推荐的算法(findAllSimPeople函数)
    person_id2num_topic = defaultdict(int)
    for topic_id in topic_id2lrs.keys():
        has_topic_person_ids = get_person_ids_by_topic_id(topic_id)
        for _id in has_topic_person_ids:
            if _id in person_ids:
                continue
            person_id2num_topic[_id] += topic_id2lrs[topic_id]
    similar_person_ids = [_id for (_id, _) in sort_dict2list(person_id2num_topic)]
    return similar_person_ids


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


def get_person_dict(all_person_ids):
    GRAPH_DAO = common.GRAPH_DAO
    person_dict = {}
    for _id in all_person_ids:
        person_dict[_id] = {'name': GRAPH_DAO.get_node_name_by_id(_id),
                            'en_name': GRAPH_DAO.get_node_en_name_by_id(_id)}
    return person_dict
