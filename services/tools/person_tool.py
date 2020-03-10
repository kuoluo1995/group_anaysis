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
