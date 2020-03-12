import gc
import numpy as np


def multidimensional_scale(num_component, data=None, _dist=None):
    if data is not None:
        num_vector, num_dim = data.shape
        _dist = np.zeros((num_vector, num_vector))
        for i in range(num_vector):
            _dist[i] = np.sum(np.square(data[i] - data), axis=1).reshape(1, num_vector)

    if _dist is not None:
        num_vector, num_vector = _dist.shape
    dist_i = np.zeros(num_vector)
    dist_j = np.zeros(num_vector)
    b = np.zeros((num_vector, num_vector))

    for i in range(num_vector):
        dist_i[i] = np.mean(_dist[i, :])
        dist_j[i] = np.mean(_dist[i, :])

    dist_ij = np.mean(_dist)
    for i in range(num_vector):
        for j in range(num_vector):
            b[i, j] = -0.5 * (_dist[i, j] - dist_i[i] - dist_j[j] + dist_ij)

    lamda, v = np.linalg.eigh(b)  # 适用于对称矩阵,矩阵特征分解 返回特征值的向量和特征向量的矩阵
    index = np.argsort(-lamda)[:num_component]
    diag_lamda = np.sqrt(np.diag(-np.sort(-lamda)[:num_component]))
    v_selected = v[:, index]
    z = v_selected.dot(diag_lamda)  # 点积
    return z
