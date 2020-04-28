import timeit

import cylouvain
import networkx as nx
from collections import defaultdict
from services import common
from services.tools.graph_tool import get_node_relevancy, get_graph_dict
from services.tools import person_tool
from services.tools.person_tool import get_all_similar_person
from services.tools.pruning_tool import lrs, getTopicWeights, compared_lrs, getPerson2TopicVec, AdaBoost
from services.tools.sentence_topic_tool import get_sentence_dict, get_sentence_id2vector, get_topic_pmi, get_topic_dict, \
    get_topic_pmi2
from tools.sort_utils import sort_dict2list
import numpy as np


def get_init_ranges():
    """得到初始化的环境参数，目前需要的只是

    Notes
    ----------
    这里的范围是通过CBDB数据库的内容查询的,但是整个函数传出来的id全是以图数据库为准

    Returns
    -------
    dynasties: dict{int:dict{string:string}}
        朝代的id（node_id）： {'name':中文的名字(node_name),'en_name': 英文名字(node_en_name)}
    status: dict{int:dict{string:string}}
        社会区分的id（node_id）： {'name':中文的名字(node_name),'en_name': 英文名字(node_en_name)}
    """
    CBDB_DAO = common.CBDB_DAO
    GRAPH_DAO = common.GRAPH_DAO
    NodeLabels = common.NodeLabels
    CBDB_DAO.start_connect()
    GRAPH_DAO.start_connect()

    dynasties = CBDB_DAO.get_all_dynasties()
    dynasties_ids = GRAPH_DAO.get_node_ids_by_label_codes(NodeLabels['dynasty'], dynasties.keys())
    dynasties = {_id: {'name': GRAPH_DAO.get_node_name_by_id(_id), 'en_name': GRAPH_DAO.get_node_en_name_by_id(_id)} for
                 _id in dynasties_ids}
    status = CBDB_DAO.get_all_status()
    status_ids = GRAPH_DAO.get_node_ids_by_label_codes(NodeLabels['status'], status.keys())
    status = {_id: {'name': GRAPH_DAO.get_node_name_by_id(_id), 'en_name': GRAPH_DAO.get_node_en_name_by_id(_id)} for
              _id in status_ids}
    address_ids = GRAPH_DAO.get_all_address()
    address = {_id: {'name': GRAPH_DAO.get_node_name_by_id(_id), 'en_name': GRAPH_DAO.get_node_en_name_by_id(_id)} for
               _id in address_ids}
    post_type_ids = GRAPH_DAO.get_all_post_types()
    post_type = {_id: {'name': GRAPH_DAO.get_node_name_by_id(_id), 'en_name': GRAPH_DAO.get_node_en_name_by_id(_id)} for
                 _id in post_type_ids}
    post_address_ids = GRAPH_DAO.get_all_post_address()
    post_address = {_id: {'name': GRAPH_DAO.get_node_name_by_id(_id),
                          'en_name': GRAPH_DAO.get_node_en_name_by_id(_id)} for _id in post_address_ids}
    office_ids = GRAPH_DAO.get_all_offices()
    office = {_id: {'name': GRAPH_DAO.get_node_name_by_id(_id), 'en_name': GRAPH_DAO.get_node_en_name_by_id(_id)} for
              _id in office_ids}
    office_type_ids = GRAPH_DAO.get_all_office_types()
    office_type = {_id: {'name': GRAPH_DAO.get_node_name_by_id(_id), 'en_name': GRAPH_DAO.get_node_en_name_by_id(_id)}
                   for _id in office_type_ids}
    entry_ids = GRAPH_DAO.get_all_entries()
    entry = {_id: {'name': GRAPH_DAO.get_node_name_by_id(_id), 'en_name': GRAPH_DAO.get_node_en_name_by_id(_id)} for
             _id in entry_ids}
    entry_type_ids = GRAPH_DAO.get_all_entry_types()
    entry_type = {_id: {'name': GRAPH_DAO.get_node_name_by_id(_id), 'en_name': GRAPH_DAO.get_node_en_name_by_id(_id)}
                  for _id in entry_type_ids}
    GRAPH_DAO.close_connect()
    CBDB_DAO.close_connect()
    return dynasties, status, address, post_type, post_address, office, office_type, entry, entry_type


def get_relation_person_by_name(person_name, ranges):
    """根据person_name和所需要的范围label来得到范围所包含的值(name)

    Notes
    ----------
    这里的范围是通过图数据库的内容查询的

    Parameters
    ----------
    ranges: dict{string:dict{string:int}}
        具体的值参考 @see services/configs/labels.yaml
    person_name : string

    Returns
    -------
    ranges: dict{string:dict{int:dict{string:string}}}
        node_label to node_id to node_name
        {node_label: {(node_id): {'name': 中文的名字(node_name), 'en_name': 英文名字(node_en_name)}}}
    """
    GRAPH_DAO = common.GRAPH_DAO
    MetaPaths = common.MetaPaths
    NodeLabels = common.NodeLabels
    GRAPH_DAO.start_connect()
    if person_name is None or type(person_name) != str or person_name == '':
        raise Exception('get_relation_person_by_name({})'.format(person_name))

    person_ids = GRAPH_DAO.get_node_ids_by_name(person_name)
    all_person_dict = list()
    for _id in person_ids:
        person_dict = defaultdict(dict)
        for _key, _items in ranges.items():
            all_paths = MetaPaths[_key].get_all_paths_by_node_id(_id)
            for _path in all_paths:
                person_ids = []
                relation_ids = []
                _label, index = list(_items.keys())[0], list(_items.values())[0]
                search_label = GRAPH_DAO.get_node_label_by_id if index == 0 else GRAPH_DAO.get_edge_label_by_id
                search_name = GRAPH_DAO.get_node_name_by_id if index == 0 else GRAPH_DAO.get_edge_name_by_id
                search_en_name = GRAPH_DAO.get_node_en_name_by_id if index == 0 else GRAPH_DAO.get_edge_en_name_by_id
                for i, word_id in enumerate(_path):
                    if i % 2 == 0 and i != 0:
                        if GRAPH_DAO.get_node_label_by_id(word_id) == NodeLabels['person']:
                            person_ids.append(word_id)
                    if i % 2 == index:
                        _label_ = search_label(word_id)
                        if _label_ == _label:
                            relation_ids.append(word_id)
                if len(person_ids) == 1 and len(relation_ids) == 1:
                    person_id = person_ids[0]
                    relation_id = relation_ids[0]
                    if person_id not in person_dict:
                        person_dict[person_id] = {'name': GRAPH_DAO.get_node_name_by_id(person_id),
                                                  'en_name': GRAPH_DAO.get_node_en_name_by_id(person_id),
                                                  'relation': list()}
                    person_dict[person_id]['relation'].append({'name': search_name(relation_id),
                                                               'en_name': search_en_name(relation_id),
                                                               'type': _key})
                else:
                    print(_path)
        person_dict[_id] = {'name': GRAPH_DAO.get_node_name_by_id(_id),
                            'en_name': GRAPH_DAO.get_node_en_name_by_id(_id),
                            'relation': [{'name': 'Y(自己)', 'en_name': 'Y(self)'}]}
        dynasty_paths = MetaPaths['朝代'].get_all_paths_by_node_id(_id)
        if len(dynasty_paths) > 0:
            dynasty_id = dynasty_paths[0][-2]
            person_dict[_id]['relation'][0]['dynasty'] = {'name': GRAPH_DAO.get_node_name_by_id(dynasty_id),
                                                          'en_name': GRAPH_DAO.get_node_en_name_by_id(dynasty_id)}
        status_paths = MetaPaths['社会区分'].get_all_paths_by_node_id(_id)
        if len(status_paths) > 0:
            status_ids = [_path[-2] for _path in status_paths]
            person_dict[_id]['relation'][0]['status'] = [{'name': GRAPH_DAO.get_node_name_by_id(status_id),
                                                          'en_name': GRAPH_DAO.get_node_en_name_by_id(status_id)} for
                                                         status_id in status_ids]
        address_paths = MetaPaths['籍贯'].get_all_paths_by_node_id(_id)
        if len(address_paths) > 0:
            address_id = address_paths[0][-2]
            person_dict[_id]['relation'][0]['address'] = {'name': GRAPH_DAO.get_node_name_by_id(address_id),
                                                          'en_name': GRAPH_DAO.get_node_en_name_by_id(address_id)}
        address_paths = MetaPaths['籍贯'].get_all_paths_by_node_id(_id)
        if len(address_paths) > 0:
            address_id = address_paths[0][-2]
            person_dict[_id]['relation'][0]['address'] = {'name': GRAPH_DAO.get_node_name_by_id(address_id),
                                                          'en_name': GRAPH_DAO.get_node_en_name_by_id(address_id)}
        all_person_dict.append(person_dict)
    GRAPH_DAO.close_connect()
    return all_person_dict


def get_person_by_ranges(dynasty_ids, min_year, max_year, is_female, statu_ids, address_ids, post_type_ids,
                         post_address_ids, office_ids, office_type_ids, entry_ids, entry_type_ids):
    """根据范围查询到所有的人群

    Notes
    ----------
    这里是通过CBDB数据库的内容查询的,但是整个函数传出来的id全是以图数据库为准

    Parameters
    ----------
    dynasty_ids: list(int)
        朝代id的集合
    min_year : int or None
    max_year : int or None
    is_female : bool or None
    statu_ids : list(int) or None
        社会区分id的集合

    Returns
    -------
    person: dict{int: dict{string:string}}
        人的id 对应的name和en_name
    """
    CBDB_DAO = common.CBDB_DAO
    GRAPH_DAO = common.GRAPH_DAO
    NodeLabels = common.NodeLabels
    CBDB_DAO.start_connect()
    GRAPH_DAO.start_connect()
    if dynasty_ids is not None:
        for i, _id in enumerate(dynasty_ids):
            dynasty_ids[i] = GRAPH_DAO.get_node_code_by_id(_id)
    if statu_ids is not None:
        for i, _id in enumerate(statu_ids):
            statu_ids[i] = GRAPH_DAO.get_node_code_by_id(_id)
    person = CBDB_DAO.get_person_by_ranges(dynasty_ids, min_year, max_year, is_female, statu_ids)
    person_ids = set(GRAPH_DAO.get_node_ids_by_label_codes(NodeLabels['person'], person.keys()))
    if address_ids is not None:
        _person_ids = set()
        for address_id in address_ids:
            _person_ids.update(GRAPH_DAO.get_person_ids_by_address_id(address_id))
        person_ids.intersection_update(_person_ids)
    if post_type_ids is not None:
        _person_ids = set()
        for post_type_id in post_type_ids:
            _person_ids.update(GRAPH_DAO.get_person_ids_by_post_type_id(post_type_id))
        person_ids.intersection_update(_person_ids)
    if post_address_ids is not None:
        _person_ids = set()
        for post_address_id in post_address_ids:
            _person_ids.update(GRAPH_DAO.get_person_ids_by_post_address_id(post_address_id))
        person_ids.intersection_update(_person_ids)
    if office_ids is not None:
        _person_ids = set()
        for office_id in office_ids:
            _person_ids.update(GRAPH_DAO.get_person_ids_by_office_id(office_id))
        person_ids.intersection_update(_person_ids)
    if office_type_ids is not None:
        _person_ids = set()
        for office_type_id in office_type_ids:
            _person_ids.update(GRAPH_DAO.get_person_ids_by_office_type_id(office_type_id))
        person_ids.intersection_update(_person_ids)
    if entry_ids is not None:
        _person_ids = set()
        for entry_id in entry_ids:
            _person_ids.update(GRAPH_DAO.get_person_ids_by_entry_id(entry_id))
        person_ids.intersection_update(_person_ids)
    if entry_type_ids is not None:
        _person_ids = set()
        for entry_type_id in entry_type_ids:
            _person_ids.update(GRAPH_DAO.get_person_ids_by_entry_type_id(entry_type_id))
        person_ids.intersection_update(_person_ids)
    person = {_id: {'name': GRAPH_DAO.get_node_name_by_id(_id), 'en_name': GRAPH_DAO.get_node_en_name_by_id(_id)} for
              _id in person_ids}
    GRAPH_DAO.close_connect()
    CBDB_DAO.close_connect()
    return person


def get_address_by_address_ids(address_ids):
    """根据人的id查询所有的地址及坐标

    Notes
    ----------
    这里是通过CBDB数据库的内容查询的,但是整个函数传出来的id全是以图数据库为准

    Parameters
    ----------
    address_ids: list(int)

    Returns
    -------
    address: dict{string, dict{string:float,string:float,string:string}}
        {person_id: [{'x_coord': x_coord, 'y_coord': y_coord, 'address_name': address_name}]
    """
    CBDB_DAO = common.CBDB_DAO
    GRAPH_DAO = common.GRAPH_DAO
    NodeLabels = common.NodeLabels
    CBDB_DAO.start_connect()
    GRAPH_DAO.start_connect()
    address_codes = list()
    if address_ids is None:
        return None
    address_ids = list(address_ids)
    for _id in address_ids:
        address_codes.append(GRAPH_DAO.get_node_code_by_id(_id))
    address = CBDB_DAO.get_address_by_address_codes(address_codes)
    address = {GRAPH_DAO.get_node_ids_by_label_codes(NodeLabels['address'], [_code])[0]: _item for _code, _item in
               address.items()}
    GRAPH_DAO.close_connect()
    CBDB_DAO.close_connect()
    return address


# 用于对比的
def get_compared_topics_by_person_ids(person_ids1, person_ids2, random_epoch=1000, min_sentence=5, max_topic=15,
                                      populate_ratio=0.4):
    # random_epoch = 2000

    person_ids = list(set(person_ids1 + person_ids2))

    print('查询topic的所有人数:{}'.format(len(person_ids)))
    start = timeit.default_timer()
    GRAPH_DAO = common.GRAPH_DAO
    GRAPH_DAO.start_connect()

    def process(pids):
        person_id2sentence_ids, sentence_id2person_id, all_sentence_dict = get_sentence_dict(pids,
                                                                                             random_epoch=random_epoch,
                                                                                             min_sentence=min_sentence)
        print('所有的描述:{}'.format(len(all_sentence_dict)))

        node_label2ids, node_id2relevancy, node_id2sentence_ids = get_node_relevancy(person_id2sentence_ids)
        topic_ids2person_ids, topic_ids2sentence_ids, all_topic_ids = get_topic_dict(node_label2ids, node_id2relevancy,
                                                                                     sentence_id2person_id,
                                                                                     node_id2sentence_ids,
                                                                                     len(person_ids),
                                                                                     len(all_sentence_dict),
                                                                                     min_sentences=min_sentence,
                                                                                     max_topic=max_topic,
                                                                                     populate_ratio=populate_ratio)
        return topic_ids2person_ids, topic_ids2sentence_ids, all_topic_ids, person_id2sentence_ids, all_sentence_dict

    t2p1, t2s1, at1, p2s1, as1 = process(person_ids1)
    t2p2, t2s2, at2, p2s2, as2 = process(person_ids2)

    # 合并的、
    as1.update(as2)
    all_sentence_dict = {**as1, **as2}
    all_topic_ids = at1.union(at2)

    topic_ids2person_ids = t2p1
    topic_ids2sentence_ids = t2s1
    for t in t2p2:
        if t not in topic_ids2person_ids:
            topic_ids2person_ids[t] = t2p2[t]
            topic_ids2sentence_ids[t] = t2s2[t]
        else:
            topic_ids2person_ids[t].update(t2p2[t])
            topic_ids2sentence_ids[t].update(t2s2[t])

    person_id2sentence_ids = p2s1
    for p in p2s2:
        if p not in p2s1:
            person_id2sentence_ids[p] = p2s2[p]
        else:
            person_id2sentence_ids[p].update(p2s2[p])

    print('1:{}'.format(timeit.default_timer() - start))
    # sentence_id2vector
    start = timeit.default_timer()
    dim2topic_id2sentence_ids2vector = get_sentence_id2vector(all_topic_ids, topic_ids2sentence_ids, num_dims=[2, 5])
    print('2:{}'.format(timeit.default_timer() - start))
    start = timeit.default_timer()
    person_id2position2d = person_tool.get_person_id2vector2d(dim2topic_id2sentence_ids2vector[5],
                                                              person_id2sentence_ids, num_dim=5)
    print('3:{}'.format(timeit.default_timer() - start))
    start = timeit.default_timer()
    # topic_pmi = get_topic_pmi(all_topic_ids, person_id2sentence_ids, topic_ids2sentence_ids, len(all_sentence_dict))
    topic_pmi = get_topic_pmi2(all_topic_ids, person_ids)
    print('4:{}'.format(timeit.default_timer() - start))
    start = timeit.default_timer()
    node_dict, edge_dict = get_graph_dict(all_sentence_dict)
    print('5:{}'.format(timeit.default_timer() - start))
    start = timeit.default_timer()

    topic_id2lrs = {_id: compared_lrs(_id, person_ids1, person_ids2) for _id in all_topic_ids}
    print('6:{}'.format(timeit.default_timer() - start))
    GRAPH_DAO.close_connect()

    return all_topic_ids, dim2topic_id2sentence_ids2vector[2], topic_pmi, person_id2position2d, node_dict, edge_dict, \
           topic_id2lrs, all_sentence_dict, dim2topic_id2sentence_ids2vector[5], person_id2sentence_ids


def get_topics_by_person_ids(person_ids, random_epoch=1500, min_sentence=5, max_topic=15, populate_ratio=0.4):
    # populate_ratio = 0.3
    """根据人的id查询所有的topic

    Notes
    ----------
    这里是通过CBDB数据库的内容查询的,但是整个函数传出来的id全是以图数据库为准

    Parameters
    ----------
    person_ids: list(int)
        所有相关人的id
    random_epoch: int
        随机游走的迭代步数
    max_topic: int
        最多多少个topic
    populate_ratio: float
        筛选的比例，topic占人口比例多少才算populate topic

    Returns
    -------
    all_topic_ids: list(int)
        topic其实就是name, 所以就是node_name对应的id集合
    label2topic_ids: dict{string: list(int)}
        label下所包含的全部topic_name的id
    topic_id2sentence_id2position1d: dict{int:dict{list(int): float}}
        topic_id下所有的描述id，并且描述id还有对应的一维位置
    topic_pmi: dict{int: dict{int: float}}
        topic的pmi矩阵 标签之间的相关性，每个Topic的连线，越高先关系越大 pmi点互信息（概率论）
    person_id2position2d: dict{int: (int,int)}
        相关人降维每个人的二维位置信息
    node_dict: dict{int:dict{string: string}}
        节点字典： {node_id: {'name': name, 'label':label, 'en_name': en_name}}
    edge_dict: dict{int:dict{string: string}}
        边字典: {edge_id: {'name': name, 'label': label, 'en_name': en_name}}
    """
    print('查询topic的所有人数:{}'.format(len(person_ids)))
    start = timeit.default_timer()
    GRAPH_DAO = common.GRAPH_DAO
    GRAPH_DAO.start_connect()

    person_id2sentence_ids, sentence_id2person_id, all_sentence_dict = get_sentence_dict(person_ids,
                                                                                         random_epoch=random_epoch,
                                                                                         min_sentence=min_sentence)
    print('所有的描述:{}'.format(len(all_sentence_dict)))

    node_label2ids, node_id2relevancy, node_id2sentence_ids = get_node_relevancy(person_id2sentence_ids)

    topic_ids2person_ids, topic_ids2sentence_ids, all_topic_ids = get_topic_dict(node_label2ids, node_id2relevancy,
                                                                                 sentence_id2person_id,
                                                                                 node_id2sentence_ids, len(person_ids),
                                                                                 len(all_sentence_dict),
                                                                                 min_sentences=min_sentence,
                                                                                 max_topic=max_topic,
                                                                                 populate_ratio=populate_ratio)

    # 强行过滤
    topic_ids2sentence_ids = {_t: set(list(ss)[:3000]) for _t, ss in topic_ids2sentence_ids.items()}

    print('1:{}'.format(timeit.default_timer() - start))
    # sentence_id2vector
    start = timeit.default_timer()
    dim2topic_id2sentence_ids2vector = get_sentence_id2vector(all_topic_ids, topic_ids2sentence_ids,
                                                              num_dims=[2, 5])  # , 5
    print('2:{}'.format(timeit.default_timer() - start))
    start = timeit.default_timer()
    # dim2topic_id2sentence_ids2vector[5], 
    person_id2position2d = person_tool.get_person_id2vector2d(dim2topic_id2sentence_ids2vector[5],
                                                              person_id2sentence_ids, num_dim=5)
    print('3:{}'.format(timeit.default_timer() - start))
    start = timeit.default_timer()
    # topic_pmi = get_topic_pmi(all_topic_ids, person_id2sentence_ids, topic_ids2sentence_ids, len(all_sentence_dict))
    topic_pmi = get_topic_pmi2(all_topic_ids, person_ids)
    print('4:{}'.format(timeit.default_timer() - start))
    start = timeit.default_timer()
    node_dict, edge_dict = get_graph_dict(all_sentence_dict)
    print('5:{}'.format(timeit.default_timer() - start))
    start = timeit.default_timer()

    # topic_id2lrs = getTopicWeights(all_topic_ids, person_ids)
    # print(topic_id2lrs)

    topic_id2lrs = {_id: lrs(_id, person_ids) for _id in all_topic_ids}
    if len(all_topic_ids) > 1:
        all_topic_ids = [item for item, _ in sort_dict2list(topic_id2lrs)]

        _, person_vec, labels = getPerson2TopicVec(all_topic_ids, person_ids)
        # print(person_vec[:10], labels[:10] )

        ada_boost_model = AdaBoost(len(all_topic_ids))
        ada_boost_model.train(person_vec, labels)

        topic_w = ada_boost_model.alphas
        # print(topic_w)
        # # 正则化
        max_w, min_w = np.max(topic_w), np.min(topic_w)
        topic_w = (topic_w - min_w) / (max_w - min_w)  # + 0.01

        topic_id2lrs = {all_topic_ids[index]: max([0, w]) for index, w in enumerate(topic_w)}

    # print(topic_id2lrs)
    for topic_id, _lrs in topic_id2lrs.items():
        topic_name = [GRAPH_DAO.get_node_name_by_id(n) for n in topic_id]
        print(topic_name, _lrs, lrs(topic_id, person_ids))

    print('6:{}'.format(timeit.default_timer() - start))
    GRAPH_DAO.close_connect()

    return all_topic_ids, dim2topic_id2sentence_ids2vector[2], topic_pmi, person_id2position2d, node_dict, edge_dict, \
           topic_id2lrs, all_sentence_dict, dim2topic_id2sentence_ids2vector[5], person_id2sentence_ids


def get_top_topic_by_sentence_ids(all_sentence_ids, min_sentence=5, max_topic=15, populate_ratio=0.6):
    GRAPH_DAO = common.GRAPH_DAO
    GRAPH_DAO.start_connect()
    person_id2sentence_ids, sentence_id2person_id = person_tool.get_person2sentence_by_sentence(all_sentence_ids)
    node_label2ids, node_id2relevancy, node_id2sentence_ids = get_node_relevancy(person_id2sentence_ids)
    topic_ids2person_ids, topic_ids2sentence_ids, all_topic_ids = get_topic_dict(node_label2ids, node_id2relevancy,
                                                                                 sentence_id2person_id,
                                                                                 node_id2sentence_ids,
                                                                                 len(person_id2sentence_ids.keys()),
                                                                                 len(all_sentence_ids),
                                                                                 min_sentences=min_sentence,
                                                                                 max_topic=max_topic,
                                                                                 populate_ratio=populate_ratio)
    topic_ids = sort_dict2list(topic_ids2person_ids)
    topic_ids = [_id[0] for _id in topic_ids]
    GRAPH_DAO.close_connect()
    return topic_ids


# 我改了get_person_id2vector2d这里有问题了
def add_topic_weights(topic_weights, topic_id2sentence_ids2vector, person_id2sentence_ids, num_dim=5):
    GRAPH_DAO = common.GRAPH_DAO
    GRAPH_DAO.start_connect()
    person_id2position2d = person_tool.get_person_id2vector2d(topic_id2sentence_ids2vector,
                                                              person_id2sentence_ids, topic_weights=topic_weights,
                                                              num_dim=num_dim)
    person_dict = person_tool.get_person_dict(person_id2position2d.keys())
    GRAPH_DAO.close_connect()
    return person_id2position2d, person_dict


def get_similar_person(person_ids, topic_weights):
    GRAPH_DAO = common.GRAPH_DAO
    GRAPH_DAO.start_connect()
    similar_person_ids = get_all_similar_person(person_ids, topic_weights)
    similar_person = person_tool.get_person_dict(similar_person_ids)
    GRAPH_DAO.close_connect()
    return similar_person


def get_person_by_draws(sql):
    NEO4J_DAO = common.NEO4J_DAO
    ids = NEO4J_DAO.query(sql.strip())
    return ids


def get_community_by_num_node_links(num_node, links):
    """
    Notes
    ----------
    这里是需要按照新库 cylouvain

    Parameters
    ----------
    num_node: int
    links: list(string)

    Returns
    -------
    partition:
    """
    graph = nx.Graph()
    graph.add_nodes_from([str(id) for id in range(0, num_node)])
    node_links = []
    for link in links:
        link = link.split('_')
        node_links.append((link[0], link[1]))  # cylouvain
    graph.add_edges_from(node_links)
    partition = cylouvain.best_partition(graph)
    # partition = None  # 暂时注释掉
    return partition
