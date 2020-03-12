import cylouvain
import gc
import networkx as nx
from collections import defaultdict
from services import common
from services.common import Model_DIM
from services.tools.graph_tool import get_node_relevancy, get_graph_dict
from services.tools.person_tool import get_person_id2position2d
from services.tools.sentence_topic_tool import get_sentence_ids_dict, get_sentence_id2relevancy, get_sentence_id2vector, \
    get_topic_id_dict, get_topic_pmi, get_sentence_id2position1d


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
    GRAPH_DAO.close_connect()
    CBDB_DAO.close_connect()
    return dynasties, status


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


def get_topics_by_person_ids(person_ids, random_epoch=100, max_topic=15, populate_ratio=0.3):
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
    node_label2ids, node_id2relevancy = get_node_relevancy(person_ids)

    person_id2sentence_ids, sentence_id2person_id, all_sentence_ids = get_sentence_ids_dict(person_ids,
                                                                                            random_epoch=random_epoch)

    sentence_id2relevancy = {_sentence_id: get_sentence_id2relevancy(_sentence_id, node_id2relevancy) for _sentence_id
                             in all_sentence_ids}

    label2topic_ids, topic_id2sentence_ids, all_topic_ids = get_topic_id_dict(node_label2ids, node_id2relevancy,
                                                                              all_sentence_ids, sentence_id2relevancy,
                                                                              sentence_id2person_id, len(person_ids),
                                                                              max_topic=max_topic,
                                                                              populate_ratio=populate_ratio)

    sentence_id2vector = get_sentence_id2vector(all_sentence_ids)

    topic_id2sentence_id2position1d = {topic_id: get_sentence_id2position1d(_sentence_ids, sentence_id2vector) for
                                       topic_id, _sentence_ids in topic_id2sentence_ids.items() if
                                       len(_sentence_ids) != 0}

    topic_pmi = get_topic_pmi(all_topic_ids, person_id2sentence_ids, topic_id2sentence_ids, all_sentence_ids)

    person_id2position2d = get_person_id2position2d(sentence_id2vector, person_id2sentence_ids,
                                                    topic_id2sentence_ids_=topic_id2sentence_ids, num_dim=Model_DIM)

    node_dict, edge_dict = get_graph_dict(all_sentence_ids)
    GRAPH_DAO.close_connect()
    return all_topic_ids, label2topic_ids, topic_id2sentence_id2position1d, topic_pmi, person_id2position2d, node_dict, edge_dict


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
    return partition
