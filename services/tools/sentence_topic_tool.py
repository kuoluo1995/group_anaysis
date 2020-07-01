import copy
import timeit

import math
import random
import numpy as np
from collections import defaultdict
from gensim import corpora, similarities

from services import common
from services.tools import person_tool
from services.tools.graph_tool import get_filtered_node
from services.tools.person_tool import get_person_ids_by_topic_ids
from tools.analysis_utils import multidimensional_scale
from tools.sort_utils import sort_dict2list, sort_by_condition

"""
Sentence 部分
========
    下面是关于Sentence的所有函数
"""


# def get_sentence_dict2(person_ids, random_epoch=100):
#     """根据人的id 随机游走找到响应的描述
#
#     Parameters
#     ----------
#     person_ids: list(int)
#         所有相关人的id
#     random_epoch: int
#         随机游走的迭代步数
#
#     Returns
#     -------
#     person_id2sentence_ids: dict{int: list(int)}
#         人的id对应到描述的id
#     sentence_id2person_id: dict{list(int): int}
#         描述的id（node_id,edge_id,node_id。。。）作为key,每个描述对应着每个人的id
#     all_sentence_ids: list(list(int))
#         所有的描述，以及描述里所有的id（node_id,edge_id,node_id。。。）
#     """
#     MetaPaths = common.MetaPaths
#
#     person_id2sentence_ids = {}  # 描述
#     sentence_id2person_id = {}
#     all_sentence_dict = {}
#     for person_id in person_ids:
#         sentence_ids = set()
#         for i in range(random_epoch):
#             meta_path = random.choice(MetaPaths)
#             _ids = meta_path.match(person_id)
#             if len(_ids) > 0:
#                 sentence_id = []
#                 for _source_id, _edge_id, _target_id in _ids:
#                     sentence_id += [_source_id, _edge_id, _target_id]
#                 sentence_id = tuple(sentence_id)  # list没法hash，所以要转化成元组
#                 sentence_ids.add(sentence_id)
#                 sentence_id2person_id[sentence_id] = person_id
#                 all_sentence_dict[sentence_id] = meta_path.name
#         person_id2sentence_ids[person_id] = sentence_ids
#     return person_id2sentence_ids, sentence_id2person_id, all_sentence_dict


def get_sentence_dict(person_ids, random_epoch=100, min_sentence=5):
    """根据人的id 随机游走找到响应的描述

    Parameters
    ----------
    person_ids: list(int)
        所有相关人的id
    random_epoch: int
        随机游走的迭代步数

    Returns
    -------
    person_id2sentence_ids: dict{int: list(int)}
        人的id对应到描述的id
    sentence_id2person_id: dict{list(int): int}
        描述的id（node_id,edge_id,node_id。。。）作为key,每个描述对应着每个人的id
    all_sentence_ids: list(list(int))
        所有的描述，以及描述里所有的id（node_id,edge_id,node_id。。。）
    """
    MetaPaths = common.MetaPaths
    GRAPH_DAO = common.GRAPH_DAO
    NodeLabels = common.NodeLabels
    person_id2sentence_ids = defaultdict(set)  # 描述
    sentence_id2person_ids = {}
    all_sentence_dict = {}
    for person_id in person_ids:
        sentence_ids = set()
        all_paths = [{tuple(sentence_id): _key for sentence_id in _path.get_all_paths_by_node_id(person_id)} for
                     _key, _path in MetaPaths.items()]  # list没法hash，所以要转化成元组
        all_paths_num = 0
        for sentence in all_paths:
            all_paths_num += len(sentence)
        if all_paths_num <= min_sentence:
            continue
        for sentence in all_paths:
            for sentence_id, sentence_type in sentence.items():
                sentence_ids.add(sentence_id)
                sentence_id2person_ids[sentence_id] = set(
                    [sentence_id[_n_i] for _n_i in range(0, len(sentence_id), 2) if
                     GRAPH_DAO.get_node_label_by_id(sentence_id[_n_i]) == NodeLabels['person']])
                all_sentence_dict[sentence_id] = sentence_type
        person_id2sentence_ids[person_id] = sentence_ids
    return person_id2sentence_ids, sentence_id2person_ids, all_sentence_dict


def get_sentence_ids_by_topic_ids(topic_id1, topic_id2, _topic_id2sentence_ids):
    """
    通过给定的topics来得到相应的sentence_ids，这里的sentence_ids是经过去重的

    :param topic_id1: tuple
    :param topic_id2: tuple
    :param _topic_id2sentence_ids: dict{int: list(list(int))} sentence_id是由node_id, edge_id, node_id。。。组成
    :return: set() 对应的所有的描述
    """
    GRAPH_DAO = common.GRAPH_DAO
    sentence_ids = _topic_id2sentence_ids[topic_id1].intersection(_topic_id2sentence_ids[topic_id2])
    _topic = [GRAPH_DAO.get_node_name_by_id(_t) for _t in (topic_id1 + topic_id2)]
    _sentences = [[GRAPH_DAO.get_node_name_by_id(_w) if i % 2 == 0 else GRAPH_DAO.get_edge_name_by_id(_w) for i, _w in
                   enumerate(_sentence_id)] for _sentence_id in sentence_ids]
    return sentence_ids


def get_sentence_id2relevancy(sentence_id_, node_id2relevancy):
    """计算描述的相似度

    Parameters
    ----------
    sentence_id_: list(int)
        所有描述的id (node_id, edge_id, node_id) 描述由三元元组组成。所以i%2==0都是node, i%2=1都是edge
    node_id2relevancy: dict{int: float}
        这是个字典，用来算描述的相似度

    Returns
    -------
    :float
        相似度的值
    """
    sentence_id2relevancy = 0
    for i, _id in enumerate(sentence_id_):
        if i % 2 == 0:
            sentence_id2relevancy += node_id2relevancy[_id]
    return sentence_id2relevancy / len(sentence_id_) * 1.5  # 排除掉边， node edge node


def get_sentence_id2position1d(sentence_ids, sentence_id2vector):
    """计算所有描述里的相似度位置

    Parameters
    ----------
    sentence_ids: list(list(int))
        所有描述，以及描述是由list组成的。里面是(node_id,edge_id,node_id。。。。)组成
    sentence_id2vector: dict{list(int):array}
        所有的描述，描述是(node_id,edge_id,node_id。。。。)组成

    Returns
    -------
    sentence_id2position1d: dict{list(int): float}
        描述id所对应的一维位置
    """
    _vectors = np.array([sentence_id2vector[_sentence_id] for _sentence_id in sentence_ids])
    positions = multidimensional_scale(1, data=_vectors)  # 一维展示数组
    sentence_id2position1d = dict()
    for i, _pos1d in enumerate(positions):
        sentence_id = sentence_ids[i]
        value = _pos1d[0]  # 一维
        sentence_id2position1d[sentence_id] = value
    return sentence_id2position1d


def get_sentence_id2vector(all_topic_ids, topic_id2sentence_ids, num_dims):
    """计算描述的相似度

    Parameters
    ----------
    all_topic_ids: list(list(int))
        所有的描述的id
    topic_id2sentence_ids: dict{int: list(list(int))}
    num_dims: list()
    Returns
    -------
    _sentence_id2vector: dict{list(int): array}
        根据描述得到相似度字典
    """
    dim2topic_ids2sentence_ids2vector = defaultdict(lambda **arg: defaultdict(dict))
    # topic_id2sentence_dist = defaultdict(dict)

    vectors = {}
    for topic_id in all_topic_ids:
        sentences_ids = list(topic_id2sentence_ids[topic_id])
        print([common.GRAPH_DAO.get_node_name_by_id(e) for e in topic_id], len(sentences_ids))
        corpus = [set([str(w) for _i, w in enumerate(sentence_id) if _i % 2 == 0]) for sentence_id in sentences_ids]
        dictionary = corpora.Dictionary(corpus)
        corpus = [dictionary.doc2bow(list(_item)) for _item in corpus]
        model = common.Model(corpus)
        sim_index = similarities.SparseMatrixSimilarity(model[corpus], num_features=len(dictionary.keys()))

        num_sentence = len(sentences_ids)
        sentence_dist = np.zeros((num_sentence, num_sentence))
        sentence2sentence_dist = defaultdict(dict)
        for _i, _node_ids in enumerate(corpus):
            sentence_dist[_i] = 1 - sim_index[model[_node_ids]]
            sentence_id = sentences_ids[_i]
            for _i2, _dist in enumerate(list(sentence_dist[_i])):
                sentence2sentence_dist[sentence_id][sentences_ids[_i2]] = _dist
        # topic_id2sentence_dist[topic_id] = sentence2sentence_dist
        # print('e')
        # sentence_dist太少了降维会失败，应该是函数的问题
        for _dim in num_dims:
            vectors[_dim] = multidimensional_scale(_dim, _dist=sentence_dist)
        for _i, sentence_id in enumerate(sentences_ids):
            for _dim in num_dims:
                dim2topic_ids2sentence_ids2vector[_dim][topic_id][sentence_id] = vectors[_dim][_i]
    return dim2topic_ids2sentence_ids2vector  # , topic_id2sentence_dist


"""
Topic
========
    下面是关于Topic的所有函数
"""


def get_topic_dict(node_label2ids, relevancy_dict, sentence_id2person_ids, node_id2sentence_ids, num_persons,
                   num_sentences, min_sentences=5, max_topic=15, populate_ratio=0.4, sub_topic_ratio=0.7,
                   difficult_ratio=0.15):
    """根据相关的人和描述，得到所有有关的topic， topic其实就是node_name

    Parameters
    ----------
    node_label2ids: dict{string: list(int)}
        每个label里包含的所有id
    relevancy_dict: dict{int: int}
        节点相似度的字典 dict{node_id:相似度}
    sentence_id2person_id: dict{list(int):int}
        描述的id及其对应的person_id
    node_id2sentence_ids: dict{int: list(list(int))}
        node_id 里所有的描述
    num_persons: int
        所有相关人的人数
    num_sentences: int
    min_sentences: int
    max_topic: int
        最多多少个topic
    populate_ratio: float
        筛选的比例，topic占人口比例多少才算populate topic

    Returns
    -------
    topic_id2person_ids: dict{int: set(int)}
        topic下所包含的全部人
    topic_id2sentence_ids: dict{int: list(int)}
        topic_id对应的所有描述，以及描述是由list组成的。里面是(node_id,edge_id,node_id。。。。)组成
    all_topic_ids: set(int)
        topic其实就是name, 所以就是node_name对应的id集合
    """
    GRAPH_DAO = common.GRAPH_DAO
    topic_id2sentence_ids, all_topic_ids = defaultdict(set), set()  # 不用defaultdict 因为不能直接变成json串
    topic_id2person_ids = defaultdict(set)
    for _label, _ids in node_label2ids.items():
        _node_id2relevancy = dict()  # node_id2relevancy是个计算当前结点里已有结点的相关性
        for _id in _ids:
            _node_id2relevancy[_id] = relevancy_dict[_id]
        _node_id2relevancy = sort_dict2list(_node_id2relevancy)
        popular_node_ids = []
        for (_node_id, _) in _node_id2relevancy:
            is_need, _id = get_filtered_node(_node_id)
            if is_need:
                popular_node_ids.append(_id)
        popular_node_ids = popular_node_ids[:max_topic]
        if _label == 'Nianhao':
            popular_node_ids = []

        # todo: 可以考虑都显示然后再取前几个
        for _node_id in popular_node_ids:
            topic_id = (_node_id,)
            sentence_ids = node_id2sentence_ids[_node_id]
            person_ids = set()
            for _sentence_id in sentence_ids:
                person_ids.update(sentence_id2person_ids[_sentence_id])
            person_ids = person_ids.intersection(num_persons) # todo test
            if len(person_ids) > len(num_persons) * populate_ratio and len(sentence_ids) > min_sentences:  # 剃掉那些不算不上群体的
                topic_id2sentence_ids[topic_id] = sentence_ids  # 小圆点
                topic_id2person_ids[topic_id] = person_ids
                all_topic_ids.add(topic_id)
    print('单个topic的数量:{}'.format(len(all_topic_ids)))

    topic_ids2sentence_ids, topic_ids2person_ids, all_topic_ids = _topic_id2topic_ids(all_topic_ids,
                                                                                      topic_id2sentence_ids,
                                                                                      sentence_id2person_ids,
                                                                                      topic_id2person_ids, num_persons,
                                                                                      num_sentences, min_sentences,
                                                                                      populate_ratio, sub_topic_ratio,
                                                                                      difficult_ratio)
    # topic_ids2sentence_ids, topic_ids2person_ids, all_topic_ids = _topic_id2topic_ids2(all_topic_ids,
    #                                                                                    topic_id2sentence_ids,
    #                                                                                    topic_id2person_ids, num_persons,
    #                                                                                    num_sentences, min_sentences,
    #                                                                                    populate_ratio,
    #                                                                                    sentence_id2person_id)
    print('总topic数量:{}'.format(len(all_topic_ids)))
    all_topic_ids = sort_by_condition(topic_ids2person_ids, topic_id2sentence_ids)[:max_topic]
    topic_ids2person_ids = {_topic: _person_ids for _topic, _person_ids in topic_ids2person_ids.items() if
                            _topic in all_topic_ids}
    topic_ids2sentence_ids = {_topic: _sentence_ids for _topic, _sentence_ids in topic_ids2sentence_ids.items() if
                              _topic in all_topic_ids}
    return topic_ids2person_ids, topic_ids2sentence_ids, set(all_topic_ids)


# 规则增长
def _topic_id2topic_ids(all_topic_ids, topic_id2sentence_ids, sentence_id2person_ids, topic_id2person_ids, num_persons,
                        num_sentences, min_sentences, populate_ratio, sub_topic_ratio=0.7, difficult_ratio=0.15):
    GRAPH_DAO = common.GRAPH_DAO
    i = 0
    while True:
        no_used_topic, new_topic_ids, remove_topic_ids = set(), set(), set()
        for topic_id1 in all_topic_ids:
            for topic_id2 in all_topic_ids:
                if topic_id1 == topic_id2:
                    continue
                new_topic_id = set(topic_id1).union(set(topic_id2))
                new_topic_id = tuple(sorted(list(new_topic_id)))
                if new_topic_id in all_topic_ids or new_topic_id in no_used_topic:
                    continue
                sentence_ids = get_sentence_ids_by_topic_ids(topic_id1, topic_id2, topic_id2sentence_ids)
                # _topic = [GRAPH_DAO.get_node_name_by_id(_t) for _t in new_topic_id]
                # _sentences = [
                #     [GRAPH_DAO.get_node_name_by_id(_w) if i % 2 == 0 else GRAPH_DAO.get_edge_name_by_id(_w) for i, _w in
                #      enumerate(_sentence_id)] for _sentence_id in sentence_ids]
                if len(sentence_ids) == 0:
                    no_used_topic.add(new_topic_id)
                    continue
                person_ids = set()
                for _sentence_id in sentence_ids:
                    if 3962 in new_topic_id and 733400 in new_topic_id and 951604 in new_topic_id:
                        __s = ''
                        for __i, __word in enumerate(_sentence_id):
                            if __i%2==0:
                                __s+=GRAPH_DAO.get_node_name_by_id(__word)
                            else:
                                __s+=GRAPH_DAO.get_edge_name_by_id(__word)
                        print(__s)
                    person_ids.update(sentence_id2person_ids[_sentence_id])
                person_ids = person_ids.intersection(num_persons)
                if len(person_ids) == 0:
                    no_used_topic.add(new_topic_id)
                    continue
                support_persons = len(person_ids) / len(num_persons)
                support_topic1 = len(topic_id2sentence_ids[topic_id1]) / num_sentences
                support_topic2 = len(topic_id2sentence_ids[topic_id2]) / num_sentences
                # lift_v = len(topic_id2sentence_ids[new_topic_id]) / num_sentences / support_topic1 / support_topic2
                if populate_ratio < support_persons and len(sentence_ids) > min_sentences:
                    # 把可以合并的子序列删去
                    if support_persons > sub_topic_ratio * support_topic1:
                        remove_topic_ids.add(topic_id1)
                    if support_persons > sub_topic_ratio * support_topic2:
                        remove_topic_ids.add(topic_id2)
                    new_topic_ids.add(new_topic_id)
                    name = [GRAPH_DAO.get_node_name_by_id(_id) for _id in new_topic_id]
                    if '苏轼' in name and  '记咏文字' in name and '著述关系类' in name:
                        print(11)
                    topic_id2person_ids[new_topic_id] = person_ids
                    topic_id2sentence_ids[new_topic_id] = sentence_ids

                else:
                    no_used_topic.add(new_topic_id)

        i += 1
        # 已经不在最开始删除了
        print('循环次数:{}, 新增topic数量:{}, 删除topic数量:{}'.format(i, len(new_topic_ids), len(remove_topic_ids)))  #
        all_topic_ids.update(new_topic_ids)
        for topic_id in remove_topic_ids:
            all_topic_ids.remove(topic_id)
        if len(new_topic_ids) == 0:
            break

    temp_all_topic_ids = set(all_topic_ids)
    for t1 in all_topic_ids:
        if t1 not in temp_all_topic_ids:
            continue
        for t2 in all_topic_ids:
            if t1 == t2 or t2 not in temp_all_topic_ids:
                continue
            long_one = t2 if len(t1) < len(t2) else t1
            short_one = t1 if len(t1) < len(t2) else t2
            if set(short_one).issubset(set(long_one)):  # 是子集
                large_pids = topic_id2person_ids[short_one]
                small_pids = topic_id2person_ids[long_one]
                diff = large_pids.difference(small_pids)
                if len(diff) / len(large_pids) < difficult_ratio:
                    if short_one in temp_all_topic_ids:
                        temp_all_topic_ids.remove(short_one)
    all_topic_ids = temp_all_topic_ids
    topic_id2person_ids = {tid: topic_id2person_ids[tid] for tid in all_topic_ids}
    return topic_id2sentence_ids, topic_id2person_ids, all_topic_ids


def _topic_id2topic_ids2(all_topic_ids, topic_id2sentence_ids, topic_id2person_ids, num_persons, num_sentences,
                         min_sentences, populate_ratio, sentence_id2person_id):
    # 学长的实现方式
    def intersect(set_a, set_b):
        return set([elm for elm in set_a if elm in set_b])

    def addInverseIndexValue(topic):
        has_topic_index = None
        # 其实可以再优化的, 但估计不是性能瓶颈
        for sub_topic in topic:
            sub_topic = (sub_topic,)
            if has_topic_index is None:
                has_topic_index = topic_id2sentence_ids[sub_topic]
                continue
            has_topic_index = intersect(has_topic_index, topic_id2sentence_ids[sub_topic])
        topic_id2sentence_ids[topic] = has_topic_index

    def addInverseIndexP(topic):
        has_topic_sentences = topic_id2sentence_ids[topic]
        has_topic_p = set()
        for sentence in has_topic_sentences:
            pid = sentence_id2person_id[sentence]
            has_topic_p.add(pid)
        topic_id2person_ids[topic] = has_topic_p

    def sortTopic(topic):
        topic = sorted(list(set(topic)))
        return tuple(topic)

    all_topic_ids = set(all_topic_ids)
    _i = 0
    while True:
        has_not_add = True

        temp_all_topics = copy.deepcopy(all_topic_ids)
        for topic1 in all_topic_ids:
            for topic2 in all_topic_ids:
                if topic1 == topic2:
                    continue
                new_topic = list(topic1) + list(topic2)
                new_topic = sortTopic(new_topic)
                new_topic = tuple(new_topic)
                if new_topic in all_topic_ids:
                    continue

                addInverseIndexValue(new_topic)
                addInverseIndexP(new_topic)

                support_p = len(topic_id2person_ids[new_topic]) / num_persons

                support_t1 = len(topic_id2sentence_ids[topic1]) / num_sentences
                support_t2 = len(topic_id2sentence_ids[topic2]) / num_sentences
                lift_v = len(topic_id2sentence_ids[new_topic]) / num_sentences / support_t1 / support_t2

                if support_p > populate_ratio:
                    has_not_add = False
                    temp_all_topics.add(new_topic)

                    # 把可以合并的子序列删去
                    if support_p > 0.9 * support_t1 and topic1 in temp_all_topics:
                        # print('r')
                        temp_all_topics.remove(topic1)
                    if support_p > 0.9 * support_t2 and topic2 in temp_all_topics:
                        temp_all_topics.remove(topic2)
        _i += 1
        print('循环次数:{}, 新增topic数量:{}'.format(_i, len(temp_all_topics) - len(all_topic_ids)))
        all_topic_ids = temp_all_topics
        if has_not_add:
            break
    return topic_id2sentence_ids, topic_id2person_ids, all_topic_ids


def get_topic_pmi(all_topic_ids, person_id2sentence_ids, topic_id2sentence_ids, num_all_sentences):
    """计算所有topic的pmi 标签之间的相关性，每个Topic的连线，越高先关系越大 pmi点互信息（概率论）

    Parameters
    ----------
    all_topic_ids: list(int)
        topic其实就是name, 所以就是node_name对应的id集合
    person_id2sentence_ids: dict{int: list(int)}
        人的id对应到描述的id
    topic_id2sentence_ids: dict{int: list(int)}
        topic_id对应的所有描述，以及描述是由list组成的。里面是(node_id,edge_id,node_id。。。。)组成
    num_all_sentences: int
        所有的描述数量

    Returns
    -------
    pmi_node: dict{int: dict{int: float}}
        topic的pmi矩阵 标签之间的相关性，每个Topic的连线，越高先关系越大 pmi点互信息（概率论）
    """
    # 统计topic
    count_x, count_xy = defaultdict(int), defaultdict(dict)
    for i, _x in enumerate(all_topic_ids):
        # start = timeit.default_timer()
        for _sentence_ids in person_id2sentence_ids.values():
            for _sentence_id in _sentence_ids:
                if _sentence_id in topic_id2sentence_ids[_x]:
                    # 每一个topic对于所有的描述
                    count_x[_x] += 1
                    break
        # print('4.1.1 {}/{}:{}'.format(i + 1, len(all_topic_ids), timeit.default_timer() - start))
        # start = timeit.default_timer()
        count_xy[_x] = defaultdict(int)
        for _y in all_topic_ids:
            for _sentence_ids in person_id2sentence_ids.values():
                has_x = has_y = False
                for _sentence_id in _sentence_ids:
                    if _sentence_id in topic_id2sentence_ids[_x]:
                        has_x = True
                    if _sentence_id in topic_id2sentence_ids[_y]:
                        has_y = True
                if has_x and has_y:
                    count_xy[_x][_y] += 1
    #     print('4.1.2 {}/{}:{}'.format(i + 1, len(all_topic_ids), timeit.default_timer() - start))
    # print('4.1:{}'.format(timeit.default_timer() - start))
    # start = timeit.default_timer()
    # 计算pmi
    pmi_node = {}
    for _x in all_topic_ids:
        pmi_node[_x] = defaultdict(int)
        for _y in all_topic_ids:
            if count_x[_x] == 0 or count_x[_y] == 0:
                pmi_node[_x][_y] = 0
                continue
            p_xy = count_xy[_x][_y] / count_x[_y]  # p(x|y)
            p_x = count_x[_x] / num_all_sentences  # p(x)
            pmi = p_xy / p_x
            pmi_node[_x][_y] = 0 if pmi == 0 or _x == _y else math.log(pmi)
    # print('4.2:{}'.format(timeit.default_timer() - start))
    return pmi_node


def get_topic_pmi2(all_topic_ids, all_person_ids):
    """计算所有topic的pmi 标签之间的相关性，每个Topic的连线，越高先关系越大 pmi点互信息（概率论）

    Parameters
    ----------
    all_topic_ids: list(int)
        topic其实就是name, 所以就是node_name对应的id集合
    person_id2sentence_ids: dict{int: list(int)}
        人的id对应到描述的id
    topic_id2sentence_ids: dict{int: list(int)}
        topic_id对应的所有描述，以及描述是由list组成的。里面是(node_id,edge_id,node_id。。。。)组成
    num_all_sentences: int
        所有的描述数量

    Returns
    -------
    pmi_node: dict{int: dict{int: float}}
        topic的pmi矩阵 标签之间的相关性，每个Topic的连线，越高先关系越大 pmi点互信息（概率论）
    """
    num_all_person = len(all_person_ids)
    # 统计topic
    count_x, count_xy = defaultdict(int), defaultdict(dict)
    for i, _x in enumerate(all_topic_ids):
        # start = timeit.default_timer()
        person_x_ids = person_tool.get_person_ids_by_topic_id(_x)
        count_x[_x] += len(person_x_ids.intersection(all_person_ids))

        # print('4.1.1 {}/{}:{}'.format(i + 1, len(all_topic_ids), timeit.default_timer() - start))
        # start = timeit.default_timer()
        count_xy[_x] = defaultdict(int)
        for _y in all_topic_ids:
            person_y_ids = person_tool.get_person_ids_by_topic_id(_y)
            person_xy_ids = person_x_ids.intersection(person_y_ids)
            count_xy[_x][_y] += len(person_xy_ids.intersection(all_person_ids))
    #     print('4.1.2 {}/{}:{}'.format(i + 1, len(all_topic_ids), timeit.default_timer() - start))
    # print('4.1:{}'.format(timeit.default_timer() - start))
    # start = timeit.default_timer()
    # 计算pmi
    pmi_node = {}
    for _x in all_topic_ids:
        pmi_node[_x] = defaultdict(int)
        for _y in all_topic_ids:
            if count_x[_x] == 0 or count_x[_y] == 0:
                pmi_node[_x][_y] = 0
                continue
            p_xy = count_xy[_x][_y] / count_x[_y]  # p(x|y)
            p_x = count_x[_x] / num_all_person  # p(x)
            pmi = p_xy / p_x
            pmi_node[_x][_y] = 0 if pmi == 0 else math.log(pmi)
    # print('4.2:{}'.format(timeit.default_timer() - start))
    return pmi_node
