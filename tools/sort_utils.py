import functools

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
    if de_nom == 0:
        return 0
    cos = num / de_nom
    return cos


def cos_dict(vector_a, vector_b):
    return 0.5 + 0.5 * cos_sim(vector_a, vector_b)


def mean_vectors(vectors):
    _sum = np.zeros(vectors[0].shape)
    for vector in vectors:
        _sum += vector
    return _sum / vectors.shape[0]


# def maxN(elms, N=None, key=lambda elm: elm):
#     if N is None:
#         N = len(elms)
#     return heapq.nlargest(N, elms, key=key)


def sort_dict2list(dict_value, value_len=False, **kwargs):
    # 从大到小
    return sorted(dict_value.items(), key=lambda _item: len(_item[1]) if value_len else _item[1], reverse=True)
    # return maxN([item for item in dict_value.items()], key=lambda item: item[1], N=N)


def sort_by_condition(dict1, dict2):
    dict1 = {_k: len(_v) for _k, _v in dict1.items()}
    dict2 = {_k: len(_v) for _k, _v in dict2.items()}

    def cmp(x, y):
        if dict1[x] < dict1[y]:
            return -1
        if dict1[x] > dict1[y]:
            return 1
        if dict2[x] < dict2[y]:
            return -1
        if dict2[x] > dict2[y]:
            return 1
        return 0

    all_topic = list(dict1.keys())
    all_topic = sorted(all_topic, key=functools.cmp_to_key(cmp), reverse=True)
    return all_topic


class MyMDS:
    def __init__(self, n_components):
        self.n_components = n_components

    def fit(self, data=None, dist=None):
        if data is not None:
            m, n = data.shape
            dist = np.zeros((m, m))
            for i in range(m):
                dist[i] = np.sum(np.square(data[i] - data), axis=1).reshape(1, m)
        if dist is not None:
            m, m = dist.shape

        disti = np.zeros(m)
        distj = np.zeros(m)
        B = np.zeros((m, m))

        for i in range(m):
            disti[i] = np.mean(dist[i, :])
            distj[i] = np.mean(dist[:, i])
        distij = np.mean(dist)
        for i in range(m):
            for j in range(m):
                B[i, j] = -0.5 * (dist[i, j] - disti[i] - distj[j] + distij)
        lamda, V = np.linalg.eigh(B)
        index = np.argsort(-lamda)[:self.n_components]
        diag_lamda = np.sqrt(np.diag(-np.sort(-lamda)[:self.n_components]))
        V_selected = V[:, index]
        Z = V_selected.dot(diag_lamda)
        return Z


def mds(n_components, data=None, dist=None):
    return MyMDS(n_components).fit(data=data, dist=dist)


def lda(data, target, n_dim):
    '''
    :param data: (n_samples, n_features)
    :param target: data class
    :param n_dim: target dimension
    :return: (n_samples, n_dims)
    '''
    data = np.array(data)
    target = np.array(target)
    clusters = np.unique(target)

    # if n_dim > len(clusters)-1:
    #     print("K is too much", n_dim, len(clusters))
    #     # print("please input again")
    #     raise Exception('K is too much')

    # within_class scatter matrix
    Sw = np.zeros((data.shape[1], data.shape[1]))
    for i in clusters:
        datai = data[target == i]
        datai = datai - datai.mean(0)
        Swi = np.mat(datai).T * np.mat(datai)
        Sw += Swi

    # between_class scatter matrix
    SB = np.zeros((data.shape[1], data.shape[1]))
    u = data.mean(0)  # 所有样本的平均值
    for i in clusters:
        Ni = data[target == i].shape[0]
        ui = data[target == i].mean(0)  # 某个类别的平均值
        SBi = Ni * np.mat(ui - u).T * np.mat(ui - u)
        SB += SBi
    # print(Sw)
    S = np.linalg.inv(Sw) * SB
    eigVals, eigVects = np.linalg.eig(S)  # 求特征值，特征向量
    eigValInd = np.argsort(eigVals)
    eigValInd = eigValInd[:(-n_dim - 1):-1]
    w = eigVects[:, eigValInd]
    # print(eigVects, eigValInd)
    data_ndim = np.dot(data, w)

    return data_ndim, w
