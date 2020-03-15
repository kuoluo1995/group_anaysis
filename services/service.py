# import cylouvain
import gc
import networkx as nx
from collections import defaultdict
from services import common
from services.common import Model_DIM
from services.tools.graph_tool import get_node_relevancy, get_graph_dict
from services.tools.person_tool import get_person_id2position2d, get_person_pmi
from services.tools.sentence_topic_tool import get_sentence_ids_dict, get_sentence_id2relevancy, get_sentence_id2vector, get_topic_id_dict, get_topic_pmi, get_sentence_id2position1d
import copy


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
    dynasties = {_id: {'name': GRAPH_DAO.get_node_name_by_id(_id), 'en_name': GRAPH_DAO.get_node_en_name_by_id(_id)} for _id in dynasties_ids}
    status = CBDB_DAO.get_all_status()
    status_ids = GRAPH_DAO.get_node_ids_by_label_codes(NodeLabels['status'], status.keys())
    status = {_id: {'name': GRAPH_DAO.get_node_name_by_id(_id), 'en_name': GRAPH_DAO.get_node_en_name_by_id(_id)} for
              _id in status_ids}
    GRAPH_DAO.close_connect()
    CBDB_DAO.close_connect()
    return dynasties, status


# 为啥这要跑45秒呀
def get_ranges_by_name(labels, person_name):
    """根据person_name和所需要的范围label来得到范围所包含的值(name)
    Notes
    ----------
    这里的范围是通过图数据库的内容查询的

    Parameters
    ----------
    labels: list(string)
        具体的值参考 @see services/configs/labels.yaml
    person_name : string

    Returns
    -------
    ranges: dict{string:dict{int:dict{string:string}}}
        node_label to node_id to node_name
        {node_label: {(node_id): {'name': 中文的名字(node_name), 'en_name': 英文名字(node_en_name)}}}
    """
    GRAPH_DAO = common.GRAPH_DAO
    GRAPH_DAO.start_connect()
    if person_name is None or type(person_name) != str or person_name == '':
        raise Exception('get_ranges_by_name({})'.format(person_name))

    person_ids = GRAPH_DAO.get_node_ids_by_name(person_name)
    ranges = defaultdict(dict)
    for _id in person_ids:
        # sub_graph = GRAPH_DAO.get_sub_graph(_id, max_depth=3)
        sub_graph = GRAPH_DAO.getSubGraph(_id, depth=3)
        for node_id in sub_graph.nodes():
            node_label = GRAPH_DAO.get_node_label_by_id(node_id)
            if node_label in labels:
                ranges[node_label][node_id] = {'name': GRAPH_DAO.get_node_name_by_id(node_id),
                                               'en_name': GRAPH_DAO.get_node_en_name_by_id(node_id)}
    GRAPH_DAO.close_connect()
    return ranges


def get_person_by_ranges(dynasty_ids, min_year, max_year, is_female, statu_ids):
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
            dynasty_ids[i] = GRAPH_DAO.get_node_code_by_id(int(_id))

    if min_year is not None:
        min_year = int(min_year)
    if max_year is not None:
        max_year = int(max_year)
    if is_female is not None and type(is_female) != bool:
        raise Exception('get_person_by_ranges({})'.format(is_female))
    if statu_ids is not None:
        for i, _id in enumerate(statu_ids):
            statu_ids[i] = GRAPH_DAO.get_node_code_by_id(int(_id))

    person = CBDB_DAO.get_person_by_ranges(dynasty_ids, min_year, max_year, is_female, statu_ids)
    person_ids = GRAPH_DAO.get_node_ids_by_label_codes(NodeLabels['person'], person.keys())
    person = {_id: {'name': GRAPH_DAO.get_node_name_by_id(_id), 'en_name': GRAPH_DAO.get_node_en_name_by_id(_id)} for
              _id in person_ids}
    GRAPH_DAO.close_connect()
    CBDB_DAO.close_connect()
    return person


def get_address_by_person_ids(person_ids):
    """根据人的id查询所有的地址及坐标
    Notes
    ----------
    这里是通过CBDB数据库的内容查询的,但是整个函数传出来的id全是以图数据库为准

    Parameters
    ----------
    person_ids: list(int)

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

    if person_ids is not None:
        person_ids = list(person_ids)
        for i, _id in enumerate(person_ids):
            person_ids[i] = GRAPH_DAO.get_node_code_by_id(_id)

    address = CBDB_DAO.get_address_by_person_codes(person_ids)
    address = {GRAPH_DAO.get_node_ids_by_label_codes(NodeLabels['person'], [_code])[0]: _item for _code, _item in
               address.items()}
    GRAPH_DAO.close_connect()
    CBDB_DAO.close_connect()
    return address


def get_topics_by_person_ids(person_ids, random_epoch=1000, max_topic=15, populate_ratio=0.4):
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
    GRAPH_DAO = common.GRAPH_DAO
    GRAPH_DAO.start_connect()

    person_id2sentence_ids, sentence_id2person_id, all_sentence_ids = get_sentence_ids_dict(person_ids, random_epoch=random_epoch)



    node_label2ids, node_id2relevancy, nid2sentences = get_node_relevancy(person_ids, person_id2sentence_ids)

    # sentence_id2relevancy = {_sentence_id: get_sentence_id2relevancy(_sentence_id, node_id2relevancy) for _sentence_id in all_sentence_ids}

    topic2person_ids, topic_id2sentence_ids, all_topic_ids = get_topic_id_dict(node_label2ids, node_id2relevancy, all_sentence_ids, sentence_id2person_id, len(person_ids), nid2sentences, max_topic=max_topic, populate_ratio=populate_ratio)
    
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
        # print(has_topic_index, topic)
        for sentence in has_topic_sentences:
            pid = sentence_id2person_id[sentence]
            has_topic_p.add(pid)
        topic2person_ids[topic] = has_topic_p

    def sortTopic(topic):
        topic = sorted(list(set(topic)))
        return tuple(topic)

    all_topic_ids = set(all_topic_ids)
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

                support_p = len(topic2person_ids[new_topic])/len(person_ids)

                support_t1 = len(topic_id2sentence_ids[topic1])/len(all_sentence_ids)
                support_t2 = len(topic_id2sentence_ids[topic2])/len(all_sentence_ids)
                lift_v = len(topic_id2sentence_ids[new_topic])/len(all_sentence_ids)/support_t1/support_t2
                
                if support_p > populate_ratio:
                    has_not_add = False
                    # print(new_topic, lift_v, support_p)
                    temp_all_topics.add(new_topic)

                    # 把可以合并的子序列删去
                    if support_p > 0.9 * support_t1 and topic1 in temp_all_topics:
                        # print('r')
                        temp_all_topics.remove(topic1)
                    if support_p > 0.9 * support_t2 and topic2 in temp_all_topics:
                        temp_all_topics.remove(topic2)

        all_topic_ids = temp_all_topics
        if has_not_add:
            break

    print([[(elm, GRAPH_DAO.get_node_name_by_id(elm), GRAPH_DAO.get_node_label_by_id(elm))  for elm in t] for t in all_topic_ids])
    # exit()
    # print(all_topic_ids)

    

    # sentence_id2vector 
    topic_id2sentence_id2position5d, topic_id2sentence_id2position1d = get_sentence_id2vector(topic_id2sentence_ids, all_topic_ids)


    # todo:这里还要有个topic的权重
    person_id2position2d = get_person_id2position2d(topic_id2sentence_id2position5d, person_id2sentence_ids, num_dim = 5)
    # print(person_id2position2d)
    # exit()

    topic_pmi = get_topic_pmi(all_topic_ids, person_id2sentence_ids, topic_id2sentence_ids, len(all_sentence_ids))

    node_dict, edge_dict = get_graph_dict(all_sentence_ids)
    GRAPH_DAO.close_connect()

    # print(node_dict, edge_dict)
    # person_pmi = get_person_pmi(person_ids, person_id2sentence_ids, len(all_sentence_ids))

    return all_topic_ids, topic_id2sentence_id2position1d,  topic_pmi, person_id2position2d, node_dict, edge_dict


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
    # partition = cylouvain.best_partition(graph)
    partition = None #暂时注释掉
    return partition
