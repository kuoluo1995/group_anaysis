import math
import random
import numpy as np
from collections import defaultdict
from gensim import corpora, similarities

from services import common
from services.tools.graph_tool import get_filtered_node
from services.tools.person_tool import get_person_ids_by_topic_ids
from tools.analysis_utils import multidimensional_scale, mds
from tools.sort_utils import sort_dict2list

"""
Sentence 部分
========
    下面是关于Sentence的所有函数
"""


def get_sentence_dict(person_ids, random_epoch=100):
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

    person_id2sentence_ids = {}  # 描述
    sentence_id2person_id = {}
    all_sentence_ids = set()
    for person_id in person_ids:
        sentence_ids = set()
        for i in range(random_epoch):
            meta_path = random.choice(MetaPaths)
            _ids = meta_path.match(person_id)
            if len(_ids) > 0:
                sentence_id = []
                for _source_id, _edge_id, _target_id in _ids:
                    sentence_id += [_source_id, _edge_id, _target_id]
                sentence_id = tuple(sentence_id)  # list没法hash，所以要转化成元组
                sentence_ids.add(sentence_id)
                sentence_id2person_id[sentence_id] = person_id
                all_sentence_ids.add(sentence_id)
        person_id2sentence_ids[person_id] = sentence_ids
    return person_id2sentence_ids, sentence_id2person_id, all_sentence_ids


def get_sentence_ids_by_topic_ids(topic_id1, topic_id2, _topic_id2sentence_ids):
    """
    通过给定的topics来得到相应的sentence_ids，这里的sentence_ids是经过去重的

    :param topic_id1: tuple
    :param topic_id1: tuple
    :param _topic_id2sentence_ids: dict{int: list(list(int))} sentence_id是由node_id, edge_id, node_id。。。组成
    :return: set() 对应的所有的描述
    """
    sentence_ids = _topic_id2sentence_ids[topic_id1].intersection(_topic_id2sentence_ids[topic_id2])
    return sentence_ids


def get_sentence_id2relevancy(sentence_id_, node_id2relevancy):
    """计算描述的相似度

    Parameters
    ----------
    sentence_id_: list(int)
        所有描述的id (node_id, edge_id, node_id) 描述由三元元组组成。所以i%3=0和i%3=2都是node, i%3=1是edge
    node_id2relevancy: dict{int: float}
        这是个字典，用来算描述的相似度

    Returns
    -------
    :float
        相似度的值
    """
    sentence_id2relevancy = 0
    for i, _id in enumerate(sentence_id_):
        if i % 3 == 0 or i % 3 == 2:
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


def get_sentence_id2vector(all_topic_ids, topic_ids2sentence_ids):
    """计算描述的相似度

    Parameters
    ----------
    all_sentence_ids: list(list(int))
        所有的描述的id

    Returns
    -------
    _sentence_id2vector: dict{list(int): array}
        根据描述得到相似度字典
    """
    topic_id2sentence_ids2vec2d = defaultdict(dict)
    topic_id2sentence_ids2vec1d = defaultdict(dict)
    for topic_ids in all_topic_ids:
        sentences_ids = topic_ids2sentence_ids[topic_ids]
        sentences_ids = list(sentences_ids)
        corpus = [set([str(w) for _i, w in enumerate(sentence_id) if _i % 3 != 1]) for sentence_id in sentences_ids]
        # todo 需要学习，以及为何这里是id而不是name?
        dictionary = corpora.Dictionary(corpus)
        corpus = [dictionary.doc2bow(list(_item)) for _item in corpus]
        model = common.Model(corpus)
        sim_index = similarities.SparseMatrixSimilarity(model[corpus], num_features=len(dictionary.keys()))

        num_sentence = len(sentences_ids)
        sentence_dist = np.zeros((num_sentence, num_sentence))
        for _i, _node_ids in enumerate(corpus):
            sentence_dist[_i] = 1 - sim_index[model[_node_ids]]

        # s_dist太少了降维会失败，应该是函数的问题
        # vec2d = mds(2, dist=s_dist)
        # vec1d = mds(1, dist=s_dist)
        # print(vec2d)
        # vec2d /= mean_vectors(vec2d)
        # vec1d /= mean_vectors(vec1d)
        vec2d = multidimensional_scale(2, _dist=sentence_dist)
        vec1d = multidimensional_scale(1, _dist=sentence_dist)

        for _i, vec in enumerate(vec2d):
            sentence = sentences_ids[_i]
            topic_id2sentence_ids2vec2d[topic_ids][sentence] = vec2d[_i]
            topic_id2sentence_ids2vec1d[topic_ids][sentence] = vec1d[_i]
    return topic_id2sentence_ids2vec2d, topic_id2sentence_ids2vec1d
    # model = common.Model

    # _sentence_id2vector = {}
    # for _sentence_id in all_sentence_ids:
    #     _sentence = graph_id2string(_sentence_id)
    #     _sentence_id2vector[_sentence_id] = model.infer_vector(_sentence)


"""
Topic
========
    下面是关于Topic的所有函数
"""


def get_topic_dict(node_label2ids, relevancy_dict, sentence_id2person_id, node_id2sentence_ids, num_persons,
                   num_sentences, max_topic=10, populate_ratio=0.3):
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
    num_person: int
        所有相关人的人数
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
    topic_id2person_ids, topic_id2sentence_ids, all_topic_ids = {}, {}, set()  # 不用defaultdict 因为不能直接变成json串
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
        # topic_ids = []
        for _node_id in popular_node_ids:
            topic_id = (_node_id,)
            sentence_ids = node_id2sentence_ids[_node_id]
            person_ids = set([sentence_id2person_id[_sentence_id] for _sentence_id in sentence_ids])
            if len(person_ids) > num_persons * populate_ratio:  # 剃掉那些不算不上群体的
                # topic_ids.append(topic_id)
                all_topic_ids.add(topic_id)
                topic_id2sentence_ids[topic_id] = sentence_ids  # 小圆点
                topic_id2person_ids[topic_id] = person_ids
        # all_topic_ids += topic_ids
    topic_ids2sentence_ids, topic_ids2person_ids, all_topic_ids = _topic_id2topic_ids(all_topic_ids,
                                                                                      topic_id2sentence_ids,
                                                                                      topic_id2person_ids, num_persons,
                                                                                      num_sentences, populate_ratio)
    return topic_ids2person_ids, topic_ids2sentence_ids, all_topic_ids


def _topic_id2topic_ids(all_topic_ids, topic_id2sentence_ids, topic_id2person_ids, num_persons, num_sentences,
                        populate_ratio):
    i = 0  # todo 最新更新
    while True:
        no_used_topic = set()
        new_topic_ids = set()
        for topic_id1 in all_topic_ids:
            for topic_id2 in all_topic_ids:
                if topic_id1 == topic_id2:
                    continue
                new_topic_id = set(topic_id1).union(set(topic_id2))
                new_topic_id = tuple(sorted(list(new_topic_id)))
                if new_topic_id in all_topic_ids or new_topic_id in no_used_topic:
                    continue
                sentence_ids = get_sentence_ids_by_topic_ids(topic_id1, topic_id2, topic_id2sentence_ids)
                if len(sentence_ids) == 0:
                    no_used_topic.add(new_topic_id)
                    continue
                person_ids = get_person_ids_by_topic_ids(topic_id1, topic_id2, topic_id2person_ids)
                if len(person_ids) == 0:
                    no_used_topic.add(new_topic_id)
                    continue
                topic_id2sentence_ids[new_topic_id] = sentence_ids
                topic_id2person_ids[new_topic_id] = person_ids
                support_persons = len(topic_id2person_ids[new_topic_id]) / num_persons

                # support_t1 = len(topic_id2sentence_ids[topic_id1]) / num_sentences
                # support_t2 = len(topic_id2sentence_ids[topic_id2]) / num_sentences
                # lift_v = len(topic_id2sentence_ids[new_topic_id]) / num_sentences / support_t1 / support_t2

                if support_persons > populate_ratio:
                    new_topic_ids.add(new_topic_id)
                else:
                    no_used_topic.add(new_topic_id)
        i += 1
        print('循环次数:{}, 新增topic数量:{}'.format(i, len(new_topic_ids)))
        if len(new_topic_ids) == 0:
            break
        all_topic_ids.update(new_topic_ids)
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
    for _x in all_topic_ids:
        for _sentence_ids in person_id2sentence_ids.values():
            for _sentence_id in _sentence_ids:
                if _sentence_id in topic_id2sentence_ids[_x]:
                    # 每一个topic对于所有的描述
                    count_x[_x] += 1
                    break

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
    return pmi_node
