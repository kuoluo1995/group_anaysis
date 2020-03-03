import math
import random
import timeit
import numpy as np
import networkx as nx
from collections import defaultdict
from services import common
from utils.analysis_utils import multidimensional_scale
from utils.sort_utils import sort_dict2list, maxN, mean_vectors, cos_dict


def get_init_ranges():
    DAO = common.DAO
    NodeLabels = common.NodeLabels

    result = {NodeLabels['dynasty']: {}, NodeLabels['status']: {}}
    for _label in result.keys():
        result[_label] = DAO.get_names_by_label(_label)
    return result


def get_ranges_by_name(name):
    DAO = common.DAO
    NodeLabels = common.NodeLabels

    person_id = DAO.get_node_id_by_name(name)
    sub_graph = DAO.get_sub_graph(person_id, max_depth=2)  # 间接关系就2个，太多了的话数据量就太大了
    result = {NodeLabels['person']: {}, NodeLabels['dynasty']: {}, NodeLabels['year']: {}, NodeLabels['gender']: {},
              NodeLabels['status']: {}}
    for node_id in sub_graph.nodes():
        node_label = DAO.get_node_label_by_id(node_id)
        if node_label in result.keys():
            result[node_label][node_id] = DAO.get_node_name_by_id(node_id)
    return result


def get_person_by_dynastie(dynastie):
    DAO = common.DAO
    NodeLabels = common.NodeLabels

    # 预备数据
    dynastie_id = DAO.get_node_id_by_name(dynastie)
    sub_graph = DAO.get_sub_graph(dynastie_id, max_depth=3)
    person_ids = set()
    # 根据年代，找到所有的人
    for node_id in sub_graph.nodes():
        node_label = DAO.get_node_label_by_id(node_id)
        if node_label == NodeLabels['person']:
            person_ids.add(node_id)
    return {'person_ids': list(person_ids)}


def delete_person_by_ranges(all_person, min_year, max_year, genders, status):
    DAO = common.DAO
    NodeLabels = common.NodeLabels

    gender_ids = []
    if genders is not None:
        gender_ids = [DAO.get_node_id_by_name(_name) for _name in genders]
    statu_ids = []
    if status is not None:
        statu_ids = [DAO.get_node_id_by_name(_name) for _name in status]
    # 根据年代，性别和社会区分赛选
    person_ids = set()
    for _id in all_person:
        person_graph = DAO.get_sub_graph(_id, max_depth=1)
        is_ok = True
        for node_id in person_graph.nodes():
            node_label = DAO.get_node_label_by_id(node_id)
            if node_label == NodeLabels['year']:
                _year = DAO.get_node_name_by_id(node_id)
                if _year != 'None':
                    _year = int(_year)
                    if min_year is not None and _year < min_year:
                        is_ok = False
                        break
                    if max_year is not None and max_year < _year:
                        is_ok = False
                        break
            if node_label == NodeLabels['gender'] and len(gender_ids) > 0 and node_id not in gender_ids:
                is_ok = False
                break
            if node_label == NodeLabels['status'] and len(statu_ids) > 0 and node_id not in statu_ids:
                is_ok = False
                break
        if is_ok:
            person_ids.add(_id)
    return {'person_ids': list(person_ids)}


def _get_sentences_dicts(person_ids, random_epoch=100):
    DAO = common.DAO
    MetaPaths = common.MetaPaths

    person_id2sentence = {}  # 描述
    sentence2person_id = {}
    all_sentences_ = set()
    for person_id in person_ids:
        _sentences = set()
        for i in range(random_epoch):
            meta_path = random.choice(MetaPaths)
            sentence_ids = meta_path.match(person_id)
            if len(sentence_ids) > 0:
                _sentence = []
                for sentence_id in sentence_ids:
                    _sentence += [DAO.get_node_name_by_id(sentence_id['source_id']),
                                  DAO.get_edge_label_by_id(sentence_id['edge_id']),
                                  DAO.get_node_name_by_id(sentence_id['target_id'])]
                _sentence = tuple(_sentence)  # list没法hash，所以要转化成元组
                _sentences.add(_sentence)
                sentence2person_id[_sentence] = person_id
                all_sentences_.add(_sentence)
        person_id2sentence[person_id] = _sentences
    return person_id2sentence, sentence2person_id, all_sentences_


def _get_node_relevancy(person_ids):  # 计算所有点的相关度
    DAO = common.DAO
    _start = timeit.default_timer()
    # name2label = {}  # 为后期加快计算做准备
    label2names = defaultdict(list)  # 为后期加快计算做准备
    # name2count_yx = defaultdict(int)
    name2relevancy = defaultdict(int)  # 相关度集合
    person_graph = {_id: DAO.get_sub_graph(_id, max_depth=2) for _id in person_ids}
    person_graph_tree = {person_id: nx.bfs_tree(sub_graph, person_id) for person_id, sub_graph in person_graph.items()}

    print('2.1:{}'.format(timeit.default_timer() - _start))
    _start = timeit.default_timer()
    # 得到所有相关结点, NodeView没法直接hashable，所以加了list
    all_related_node_ids = []
    for _, _graph in person_graph.items():
        all_related_node_ids += _graph.nodes()
    all_related_node_ids = set(all_related_node_ids)
    print('2.2:{}'.format(timeit.default_timer() - _start))

    _start = timeit.default_timer()
    for _id in all_related_node_ids:
        is_need, node_name, node_label = _get_filtered_name_label(_id)
        if is_need:  # 检测是否被过滤掉了？
            # 计算结点的相关值
            count_yx = 0  # count(y,x)
            relevancy_yx = 0  # 相关度值
            for _person_id, _sub_graph in person_graph.items():
                _sub_graph_tree = person_graph_tree[_person_id]
                if _id in _sub_graph:
                    count_yx += 1
                    depth = nx.shortest_path_length(_sub_graph_tree, _person_id, _id)
                    relevancy_yx += 1 / math.log(depth + 2)
            label2names[node_label].append(node_name)
            # name2label[node_name] = node_label
            # name2count_yx[node_name] += count_yx  # /len(id2p_subg.keys())
            name2relevancy[node_name] += relevancy_yx
    # return label2names, name2count_yx, name2relevancy
    print('2.3:{}'.format(timeit.default_timer() - _start))
    return label2names, name2relevancy


def _get_sentence_relevancy(sentence_, name2relevancy):
    sentence_relevancy = 0
    for _word in sentence_:
        sentence_relevancy += name2relevancy[_word]  # if _word in name2relevancy.keys() else 0
    return sentence_relevancy / len(sentence_)


# 筛选结点,进行加快计算 这里有两块地方都用了
def _get_filtered_name_label(id_=None, name_=None, label_=None):
    DAO = common.DAO
    NodeLabels = common.NodeLabels

    if id_ is not None and name_ is None:
        name_ = DAO.get_node_name_by_id(id_)
    if name_ in [None, 'None', '0', '未详', '[未详]']:
        return False, None, None
    if id_ is not None and label_ is None:
        label_ = DAO.get_node_label_by_id(id_)
    if label_ in [NodeLabels['post_type'], NodeLabels['address_type']]:  # 这几个label做topic没意义
        return False, None, None
    return True, name_, label_


# 多少能算显著特性
def _get_topics(label2names, name2relevancy, all_sentences_, sentence2relevancy, sentence2person_id, len_people,
                max_topic=15):
    label2topics = {}
    topic2sentences_ = {}
    all_topics_ = list()
    for _label, _names in label2names.items():
        _name2relevancy = dict()  # name2relevancy是个字典，而_name2relevancy是个计算当前结点里已有结点的相关性
        for _name in _names:
            _name2relevancy[_name] = name2relevancy[_name]  # if _name in name2relevancy.keys() else 0
        _name2relevancy = sort_dict2list(_name2relevancy)[:max_topic]  # dict2list
        _topics = list()
        for (_name, _) in _name2relevancy:
            sentences = [_sentence for _sentence in all_sentences_ if _name in _sentence]
            sentences = maxN(sentences, key=lambda item: sentence2relevancy[item])
            _person_ids = set([sentence2person_id[_sentence] for _sentence in sentences])
            if len(_person_ids) > len_people * 0.3:  # 剃掉那些不算不上群体的
                _topics.append(_name)
                topic2sentences_[_name] = sentences  # 小圆点
        label2topics[_label] = _topics
        all_topics_ += _topics
    return label2topics, topic2sentences_, all_topics_


# 计算节点
# 改成了同一个人中出现的概率
# 标签之间的相关性，每个Topic的连线，越高先关系越大 pmi点互信息（概率论）
def _get_topics_pmi(all_topics_, person_id2sentences_, topic2sentences_, all_sentences_):
    # 统计topic
    count_x = defaultdict(int)
    count_xy = defaultdict(dict)  # x和y
    for _x in all_topics_:
        count_xy[_x] = defaultdict(int)
        for _sentences in person_id2sentences_.values():
            for _sentence in _sentences:
                if _sentence in topic2sentences_[_x]:  # 每一个topic对于所有的描述
                    count_x[_x] += 1
                    break
        for _y in all_topics_:
            for _sentences in person_id2sentences_.values():
                has_x = has_y = False
                for _sentence in _sentences:
                    if _sentence in topic2sentences_[_x]:
                        has_x = True
                    if _sentence in topic2sentences_[_y]:
                        has_y = True
                if has_x and has_y:
                    count_xy[_x][_y] += 1
    # 计算pmi
    pmi_node = {}
    for _x in all_topics_:
        pmi_node[_x] = defaultdict(int)
        for _y in all_topics_:
            if count_x[_x] == 0 or count_x[_y] == 0:
                pmi_node[_x][_y] = 0
                continue
            p_xy = count_xy[_x][_y] / count_x[_y]  # p(x|y)
            p_x = count_x[_x] / len(all_sentences_)  # p(x)
            pmi = p_xy / p_x
            if pmi == 0 or _x == _y:
                pmi_node[_x][_y] = 0
            else:
                pmi_node[_x][_y] = math.log(pmi)
    return pmi_node


def _get_sentence2vector(all_sentences_):
    model = common.Model

    _sentence2vector = {}
    for _sentence in all_sentences_:
        _sentence2vector[_sentence] = model.infer_vector(_sentence)
    return _sentence2vector


def _get_topic2sentence_position(sentence2vector_, topic2sentences_):
    topic2sentence_positions = {}
    for _topic, _sentences in topic2sentences_.items():
        if len(_sentences) == 0:
            continue
        _vectors = np.array([sentence2vector_[_sentence] for _sentence in _sentences])
        positions = multidimensional_scale(1, data=_vectors)  # 一维展示
        sentences_position = dict()
        for i, _pos1d in enumerate(positions):
            s = '.'.join(_sentences[i])
            y = _pos1d[0]  # 一维
            sentences_position[s] = y
        topic2sentence_positions[_topic] = sentences_position
    return topic2sentence_positions


# 计算人物相似度方案一(学长)
def _get_person2position2d_1(sentence2vector_, person_id2sentences_, topic2sentences_, num_dim=100, **kwargs):
    DAO = common.DAO

    num_topic = len(topic2sentences_.keys())
    person_id2vector = {person_id: np.zeros(num_topic * num_dim) for person_id in person_id2sentences_.keys()}
    _i = 0
    for _topic, _sentences in topic2sentences_.items():
        _topic_vectors = np.array([sentence2vector_[_sentence] for _sentence in _sentences])
        _mean = mean_vectors(_topic_vectors)
        for person_id in person_id2sentences_.keys():
            max_vector = _mean
            _vectors = [sentence2vector_[_sentence] for _sentence in person_id2sentences_[person_id] if
                        _sentence in _sentences]
            if len(_vectors) > 0:
                max_vector = max(_vectors, key=lambda item: cos_dict(item, _mean))
            # 可以在这里加个维度的权重参数
            person_id2vector[person_id][_i * num_dim:(_i + 1) * num_dim] = max_vector
        _i += 1
    _vectors = np.array([_vector for _, _vector in person_id2vector.items()])
    positions = multidimensional_scale(2, data=_vectors)

    _i = 0
    person2positions = dict()
    for _person_id, _ in person_id2vector.items():
        name = DAO.get_node_name_by_id(_person_id)
        person2positions[_person_id] = {'name': name, 'position': (positions[_i][0], positions[_i][1])}
        _i += 1
    return person2positions


# 计算人物相似度方案二
def _get_person2position2d_2(sentence2vector_, person_id2sentences_, **kwargs):
    DAO = common.DAO

    _vectors = list()
    for _, _sentences in person_id2sentences_.items():
        sentence_vectors = np.array([sentence2vector_[_sentence] for _sentence in _sentences])
        _mean = mean_vectors(sentence_vectors)
        _vectors.append(_mean)
    _position2ds = multidimensional_scale(2, data=np.array(_vectors))

    _i = 0
    person2positions = dict()
    for _person_id, _ in person_id2sentences_.items():
        person2positions[_person_id] = {'name': DAO.get_node_name_by_id(_person_id), 'position': _position2ds[_i]}
        _i += 1
    return person2positions


def get_topics_by_person_ids(person_ids, max_topic=15):
    start = timeit.default_timer()
    person_id2sentences, sentence2person_id, all_sentences = _get_sentences_dicts(person_ids, random_epoch=100)
    print('1:{}'.format(timeit.default_timer() - start))

    start = timeit.default_timer()
    # label2names, name2count_yx, name2relevancy = _get_node_relevancy(person_ids)
    label2names, name2relevancy = _get_node_relevancy(person_ids)
    print('2:{}'.format(timeit.default_timer() - start))

    start = timeit.default_timer()
    sentence2relevancy = {_sentence: _get_sentence_relevancy(_sentence, name2relevancy) for _sentence in all_sentences}
    print('3:{}'.format(timeit.default_timer() - start))

    start = timeit.default_timer()
    label2topics, topic2sentences, all_topics = _get_topics(label2names, name2relevancy, all_sentences,
                                                            sentence2relevancy, sentence2person_id, len(person_ids),
                                                            max_topic=max_topic)
    print('4:{}'.format(timeit.default_timer() - start))

    start = timeit.default_timer()
    pmi_node = _get_topics_pmi(all_topics, person_id2sentences, topic2sentences, all_sentences)
    print('5:{}'.format(timeit.default_timer() - start))

    start = timeit.default_timer()
    sentence2vector = _get_sentence2vector(all_sentences)
    print('6:{}'.format(timeit.default_timer() - start))

    start = timeit.default_timer()
    topic2sentence_positions = _get_topic2sentence_position(sentence2vector, topic2sentences)
    print('7:{}'.format(timeit.default_timer() - start))

    start = timeit.default_timer()
    person2positions = _get_person2position2d_1(sentence2vector, person_id2sentences, topic2sentences_=topic2sentences)
    print('8:{}'.format(timeit.default_timer() - start))
    return {'all_topics': all_topics, 'label2topics': label2topics, 'pmi_node': pmi_node,
            'topic2sentence_positions': topic2sentence_positions, 'person2positions': person2positions}
