import heapq

import math
import numpy as np

from services import common
from services.tools import person_tool


def cos_sim(vector_a, vector_b):
    """
    计算两个向量之间的余弦相似度
    :param vector_a: 向量 a
    :param vector_b: 向量 b
    :return: sim
    """
    vector_a = np.mat(vector_a)
    vector_b = np.mat(vector_b)
    num = float(vector_a * vector_b.T)
    de_nom = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
    if de_nom == 0:  # todo checked
        return 1
    cos = num / de_nom
    return cos


def cos_dict(vector_a, vector_b):
    return 0.5 + 0.5 * cos_sim(vector_a, vector_b)


def mean_vectors(vectors):
    _sum = np.zeros(vectors[0].shape)
    for vector in vectors:
        _sum += vector
    return _sum / vectors.shape[0]


def maxN(elms, N=None, key=lambda elm: elm):
    if N is None:
        N = len(elms)
    return heapq.nlargest(N, elms, key=key)


def sort_dict2list(dict_value, N=None):
    # 从大到小
    return maxN([item for item in dict_value.items()], key=lambda item: item[1], N=N)


def sort_set2list(_set):
    return sorted(list(_set))


# 计算LRS
def LRS(topic_id, person_ids):
    m_z = len(person_ids) / common.NUM_ALL_PERSON
    m_f = 1 - m_z

    has_topic_person_ids = person_tool.get_person_ids_by_topic_id(topic_id)
    has_topic_person_ids_len = len(has_topic_person_ids)
    # todo 似乎有问题?
    if has_topic_person_ids_len == 0:
        return 0
    m_gz = len([_id for _id in person_ids if _id in has_topic_person_ids]) / has_topic_person_ids_len
    m_gf = 1 - m_gz

    return 2 * (m_gz * math.log(m_gz / m_z) + m_gf * math.log(m_gf / m_f)) * has_topic_person_ids_len
