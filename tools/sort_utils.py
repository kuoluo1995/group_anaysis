import heapq
import numpy as np


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
