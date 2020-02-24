import math
import random
import timeit
import networkx as nx
from collections import defaultdict
from services import common


def get_init_ranges():
    DAO = common.DAO
    NodeLabels = common.NodeLabels

    result = {NodeLabels['dynasty']: {}, NodeLabels['gender']: {}, NodeLabels['status']: {}}
    for _label in result.keys():
        result[_label] = DAO.get_names_by_label(_label)
    return result


def get_ranges_by_name(name):
    DAO = common.DAO
    NodeLabels = common.NodeLabels

    person_id = DAO.get_node_id_by_name(name)
    sub_graph = DAO.get_sub_graph(person_id, max_depth=2)  # 间接关系就2个，太多了的话数据量就太大了
    result = {NodeLabels['person']: {}, NodeLabels['dynasty']: {}, NodeLabels['gender']: {}, NodeLabels['status']: {}}
    for node_id in sub_graph.nodes():
        node_label = DAO.get_node_label_by_id(node_id)
        if node_label in result.keys():
            result[node_label][node_id] = DAO.get_node_name_by_id(node_id)
    return result


# todo 待朝代更新后再检测
def get_person_by_ranges(dynastie, min_year, max_year, genders, status):
    DAO = common.DAO
    NodeLabels = common.NodeLabels

    # 预备数据
    dynastie_id = DAO.get_node_id_by_name(dynastie)
    gender_ids = []
    if genders is not None:
        gender_ids = [DAO.get_node_id_by_name(_name) for _name in genders]
    statu_ids = []
    if status is not None:
        statu_ids = [DAO.get_node_id_by_name(_name) for _name in status]

    sub_graph = DAO.get_sub_graph(dynastie_id, max_depth=1)
    all_person = set()
    # 根据年代，找到所有的人
    for node_id in sub_graph.nodes():
        node_label = DAO.get_node_label_by_id(node_id)
        if node_label == NodeLabels['person']:
            all_person.add(node_id)
    # 根据年代，性别和社会区分赛选
    person_ids = set()
    for _id in all_person:
        person_graph = DAO.get_sub_graph(_id, max_depth=1)
        checked = True
        for node_id in person_graph.nodes():
            node_label = DAO.get_node_label_by_id(node_id)
            if node_label == NodeLabels['year']:
                _year = int(DAO.get_node_name_by_id(node_id))
                if min_year is not None and _year < min_year:
                    checked = False
                    break
                if max_year is not None and max_year < _year:
                    checked = False
                    break
            if node_label == NodeLabels['gender'] and node_id not in gender_ids:
                checked = False
                break
            if node_label == NodeLabels['status'] and node_id not in statu_ids:
                checked = False
                break
        if checked:
            person_ids.add(_id)
    # 再来筛选topic
    return {'person_ids': list(person_ids)}


def _get_sentences_dicts(person_ids, random_epoch=100):
    DAO = common.DAO
    MetaPaths = common.MetaPaths

    person_id2sentence = {}  # 描述
    sentence2person_id = {}
    all_sentences = set()
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
                all_sentences.add(_sentence)
        person_id2sentence[person_id] = _sentences
    return person_id2sentence, sentence2person_id, all_sentences


def _get_node_relevancy(person_ids):  # 计算所有点的相关度
    DAO = common.DAO

    # name2label = {}  # 为后期加快计算做准备
    label2names = defaultdict(list)  # 为后期加快计算做准备
    # name2count_yx = defaultdict(int)
    name2relevancy = defaultdict(int)  # 相关度集合
    person_graph = {_id: DAO.get_sub_graph(_id, max_depth=2) for _id in person_ids}
    person_graph_tree = {person_id: nx.bfs_tree(sub_graph, person_id) for person_id, sub_graph in person_graph.items()}
    # 得到所有相关结点, NodeView没法直接hashable，所以加了list
    all_related_node_ids = []
    for _, _graph in person_graph.items():
        all_related_node_ids += _graph.nodes()
    all_related_node_ids = set(all_related_node_ids)

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
def _get_topics(label2names, name2relevancy, all_sentences, sentence2relevancy, sentence2person_id, len_people,
                max_topic=15):
    label2topics = {}
    topic2sentences = {}
    all_topics = list()
    for _label, _names in label2names.items():
        _name2relevancy = dict()  # name2relevancy是个字典，而_name2relevancy是个计算当前结点里已有结点的相关性
        for _name in _names:
            _name2relevancy[_name] = name2relevancy[_name]  # if _name in name2relevancy.keys() else 0
        _name2relevancy = common.sort_dict2list(_name2relevancy)[:max_topic]  # dict2list
        _topics = list()
        for (_name, _) in _name2relevancy:
            sentences = [_sentence for _sentence in all_sentences if _name in _sentence]
            sentences = common.maxN(sentences, key=lambda item: sentence2relevancy[item])
            _person_ids = set([sentence2person_id[_sentence] for _sentence in sentences])
            if len(_person_ids) > len_people * 0.3:  # 剃掉那些不算不上群体的
                _topics.append(_name)
                topic2sentences[_name] = sentences  # 小圆点
        label2topics[_label] = _topics
        all_topics += _topics
    return label2topics, topic2sentences, all_topics


# 计算节点
# 改成了同一个人中出现的概率
# 标签之间的相关性，每个Topic的连线，越高先关系越大 pmi点互信息（概率论）
def _get_topics_pmi(all_topics, person_id2sentences, topic2sentences, all_sentences):
    # 统计topic
    count_x = defaultdict(int)
    count_xy = defaultdict(int)  # x和y
    for _x in all_topics:
        count_xy[_x] = defaultdict(int)
        for _sentences in person_id2sentences.values():
            for _sentence in _sentences:
                if _sentence in topic2sentences[_x]:  # 每一个topic对于所有的描述
                    count_x[_x] += 1
                    break
        for _y in all_topics:
            for _sentences in person_id2sentences.values():
                has_x = has_y = False
                for _sentence in _sentences:
                    has_x = True if _sentence in topic2sentences[_x] else False
                    has_y = True if _sentence in topic2sentences[_y] else False
                if has_x and has_y:
                    count_xy[_x][_y] += 1
    # 计算pmi
    pmi_node = {}
    for _x in all_topics:
        pmi_node[_x] = defaultdict(int)
        for _y in all_topics:
            if count_x[_x] == 0 or count_x[_y] == 0:
                pmi_node[_x][_y] = 0
                continue
            p_xy = count_xy[_x][_y] / count_x[_y]  # p(x|y)
            p_x = count_x[_x] / len(all_sentences)  # p(x)
            pmi = p_xy / p_x
            if pmi == 0 or _x == _y:
                pmi_node[_x][_y] = 0
            else:
                pmi_node[_x][_y] = math.log(pmi)
    return pmi_node


def get_topics_by_person_ids(person_ids, max_topic=15):
    # start = timeit.default_timer()
    person_id2sentences, sentence2person_id, all_sentences = _get_sentences_dicts(person_ids, random_epoch=100)
    # print('1:{}'.format(timeit.default_timer() - start))
    # start = timeit.default_timer()
    # label2names, name2count_yx, name2relevancy = _get_node_relevancy(person_ids)
    label2names, name2relevancy = _get_node_relevancy(person_ids)
    # print('2:{}'.format(timeit.default_timer() - start))
    # start = timeit.default_timer()
    sentence2relevancy = {_sentence: _get_sentence_relevancy(_sentence, name2relevancy) for _sentence in all_sentences}
    # print('3:{}'.format(timeit.default_timer() - start))
    # start = timeit.default_timer()
    label2topics, topic2sentences, all_topics = _get_topics(label2names, name2relevancy, all_sentences,
                                                            sentence2relevancy, sentence2person_id, len(person_ids),
                                                            max_topic=max_topic)

    pmi_node = _get_topics_pmi(all_topics, person_id2sentences, topic2sentences, all_sentences)
    # print('4:{}'.format(timeit.default_timer() - start))
    return {'all_topics': all_topics, 'pmi_node': pmi_node, 'topic2sentences': topic2sentences,
            'label2topics': label2topics}
