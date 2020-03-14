import heapq

import gc
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
    # print(vectors)
    # print(vectors[0], vectors[0].shape)
    _sum = np.zeros(vectors[0].shape)
    for vector in vectors:
        _sum += vector
    return _sum/vectors.shape[0]


def maxN(elms, N=None, key=lambda elm: elm):
    if N is None:
        N = len(elms)
    return heapq.nlargest(N, elms, key=key)


def sort_dict2list(dict_value, N=None):
    # 从大到小
    return maxN([item for item in dict_value.items()], key=lambda item: item[1], N=N)

def intersect(set_a, set_b):
    return set([elm for elm in set_a if elm in set_b])

class MyMDS:
    def __init__(self,n_components):
        self.n_components=n_components
    
    def fit(self, data = None, dist = None):
        if data is not None:
            m, n=data.shape
            dist=np.zeros((m,m))
            for i in range(m):
                dist[i]=np.sum(np.square(data[i]-data),axis=1).reshape(1,m)   
        if dist is not None:
            m, m = dist.shape

        disti=np.zeros(m)
        distj=np.zeros(m)
        B=np.zeros((m,m))

        for i in range(m):
            disti[i]=np.mean(dist[i,:])
            distj[i]=np.mean(dist[:,i])
        distij=np.mean(dist)
        for i in range(m):
            for j in range(m):
                B[i,j] = -0.5*(dist[i,j] - disti[i] - distj[j] + distij)
        lamda,V=np.linalg.eigh(B)
        index=np.argsort(-lamda)[:self.n_components]
        diag_lamda=np.sqrt(np.diag(-np.sort(-lamda)[:self.n_components]))
        V_selected=V[:,index]
        Z=V_selected.dot(diag_lamda)
        return Z

def mds(n_components, data = None, dist = None):
    return MyMDS(n_components).fit(data = data, dist = dist)