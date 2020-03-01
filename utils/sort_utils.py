import heapq


def maxN(elms, N=None, key=lambda elm: elm):
    if N is None:
        N = len(elms)
    return heapq.nlargest(N, elms, key=key)


def sort_dict2list(dict_value, N=None):
    # 从大到小
    return maxN([item for item in dict_value.items()], key=lambda item: item[1], N=N)