import heapq

from services.dao import SqliteGraphDAO
from services.model.meta import build_meta_paths
from utils import yaml_utils

_labels = yaml_utils.read('./services/configs/labels.yaml')
NodeLabels = _labels['node']
EdgeLabels = _labels['edge']
DAO = SqliteGraphDAO()
MetaPaths = build_meta_paths('./services/configs/meta_paths.yaml')


def maxN(elms, N=None, key=lambda elm: elm):
    if N is None:
        N = len(elms)
    return heapq.nlargest(N, elms, key=key)


def sort_dict2list(dict_value, N=None):
    # 从大到小
    return maxN([item for item in dict_value.items()], key=lambda item: item[1], N=N)
