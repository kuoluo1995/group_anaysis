import json
import sqlite3
import threading
import time
from collections import defaultdict

import networkx as nx
from pathlib import Path

from py2neo import Graph

from services import common
from services.tools.sentence_topic_tool import get_sentence_dict
from tools import yaml_utils
from tools.shell_utils import Shell

ip = 'bolt://localhost:7687'
username = 'neo4j'
password = '123456'


def get_whole_graph():
    print('开始读取图数据库')

    def multiThreadLoad(func, epoch):
        ts = []
        # 44
        for i in range(epoch):
            if i % 10 == 0 and i != 0:
                print('{}的第{}代:'.format(func, i))
            t = threading.Thread(target=func, args=(i,))
            t.start()
            ts.append(t)
            time.sleep(1)

        for t in ts:
            t.join()

    def loadEdges(time, num_per_time=100000):
        query = ''' MATCH (n1)-[r]->(n2)
                    RETURN id(n1), id(n2), id(r), type(r), r.name
                    SKIP {} LIMIT {} '''.format(time * num_per_time, num_per_time)
        results = neo_graph.run(query).data()
        for node_data in results:
            # 如果该关系没有访问过
            n1_id = node_data['id(n1)']
            n2_id = node_data['id(n2)']

            r_type = node_data['type(r)']
            r_id = node_data['id(r)']
            r_name = node_data['r.name']
            r_en_name = ''  # todo feature in english
            graph.add_edge(n1_id, n2_id, r_id=r_id)
            rel2data[r_id] = (r_type, r_name, r_en_name)

    def loadNodes(time, num_per_time=100000):
        query = ''' MATCH (n)
                    RETURN id(n), labels(n), n.name, n.en_name, n.code
                    SKIP {} LIMIT {} '''.format(time * num_per_time, num_per_time)
        results = neo_graph.run(query).data()
        for node_data in results:
            # 如果该关系没有访问过
            # print(node_data)
            n_id = node_data['id(n)']

            labels = node_data['labels(n)']
            if len(labels) != 1:
                # print(node_data)  #有些啥都没有的节点，应该是没用的节点
                n_type = ''
            else:
                n_type = labels[0]
            n_name = node_data['n.name']
            n_en_name = node_data['n.en_name']
            n_code = node_data['n.code']
            if n_id in node2data:
                print(node2data[n_id], (n_type, n_name, n_en_name, n_code), n_id, '重复了')
            node2data[n_id] = (n_type, n_name, n_en_name, n_code)

    neo_graph = Graph(ip, username=username, password=password)
    graph = nx.MultiDiGraph()
    node2data = {}
    rel2data = {}
    # multiThreadLoad(loadEdges, 3)
    # multiThreadLoad(loadNodes, 3)
    multiThreadLoad(loadEdges, 100)
    print('所有边加载完')
    multiThreadLoad(loadNodes, 15)
    print('所有的点数量:{};所有的边数量{}'.format(graph.number_of_nodes(), graph.number_of_edges()))
    return graph, node2data, rel2data


def save2sqlite(graph, node2data, rel2data, db_path):
    print('开始保存图数据库内容到LiteSQL')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE graph
                (
                    source BIGINT NOT NULL,
                    target BIGINT NOT NULL,
                    r_id BIGINT NOT NULL,
                    data TEXT NOT NULL
                );
            ''')
    c.execute('''CREATE TABLE node2data
                (
                    id BIGINT PRIMARY KEY,
                    label TEXT NOT NULL,
                    name TEXT,
                    en_name TEXT,
                    code BIGINT,
                    data TEXT NOT NULL
                );
            ''')
    c.execute('''CREATE TABLE rel2data
                (
                    id BIGINT PRIMARY KEY,
                    label TEXT NOT NULL,
                    name TEXT,
                    en_name TEXT,
                    data TEXT NOT NULL
                );
            ''')
    # 还要加个name的
    c.execute('''CREATE INDEX source_index ON graph (source)''')
    c.execute('''CREATE INDEX target_index ON graph (target)''')
    c.execute('''CREATE INDEX r_id_index ON graph (r_id)''')
    c.execute('''CREATE INDEX node_code_index ON node2data (code)''')
    c.execute('''CREATE INDEX node_label_index ON node2data (label)''')
    c.execute('''CREATE INDEX node_label_code_index ON node2data (label, code)''')
    c.execute('''CREATE INDEX rel_label_index ON rel2data (label)''')

    for source, target, key in graph.edges(keys=True):
        data = graph[source][target][key]
        r_id = data['r_id']
        c.execute("INSERT INTO graph VALUES (?,?,?,?)", (source, target, r_id, json.dumps({})))

    for _id in node2data:
        label, name, en_name, n_code = node2data[_id]
        c.execute("INSERT INTO node2data VALUES (?,?,?,?,?,?)", (_id, label, name, en_name, n_code, json.dumps({})))

    for _id in rel2data:
        label, name, en_name = rel2data[_id]
        c.execute("INSERT INTO rel2data VALUES (?,?,?,?,?)", (_id, label, name, en_name, json.dumps({})))
    conn.commit()

    print('graph is save')


def insert_node2person2count(db_path):
    # 建立反向查询表
    print('create node2person2count start')
    GRAPH_DAO = common.GRAPH_DAO
    NodeLabels = common.NodeLabels
    GRAPH_DAO.start_connect()
    node_id2person_ids = defaultdict(lambda **arg: defaultdict(int))
    person_ids = GRAPH_DAO.get_node_ids_by_label(NodeLabels['person'])
    num_persons = len(person_ids)
    for _i, person_id in enumerate(person_ids):
        print('\r node2person2count {}/{}'.format(_i + 1, num_persons), end='')
        person_id2sentence_ids, _, _ = get_sentence_dict([person_id], random_epoch=1000)
        sentence_ids = person_id2sentence_ids[person_id]
        if len(sentence_ids) < 10:
            continue
        for sentence_id in sentence_ids:
            node_ids = set([word_id for _j, word_id in enumerate(sentence_id) if _j % 2 == 0])
            for node_id in node_ids:
                node_id2person_ids[node_id][person_id] += 1
    GRAPH_DAO.close_connect()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE node2person2count
                (
                    node_id BIGINT PRIMARY KEY,
                    person_id2count TEXT NOT NULL
                );
            ''')
    for node_id, person_id2count in node_id2person_ids.items():
        c.execute("INSERT INTO node2person2count VALUES (?,?)", (int(node_id), json.dumps(person_id2count)))
    conn.commit()
    print('node2person2count finish')


def insert_condition2person(db_path):
    # 建立反向查询表
    print('create condition2person start')
    GRAPH_DAO = common.GRAPH_DAO
    NodeLabels = common.NodeLabels
    MetaPaths = common.MetaPaths
    GRAPH_DAO.start_connect()
    person_ids = GRAPH_DAO.get_node_ids_by_label(NodeLabels['person'])
    address2person_ids = defaultdict(set)
    post_type2person_ids = defaultdict(set)
    post_address2person_ids = defaultdict(set)
    office2person_ids = defaultdict(set)
    office_type2person_ids = defaultdict(set)
    entry2person_ids = defaultdict(set)
    entry_type2person_ids = defaultdict(set)
    num_persons = len(person_ids)
    for _i, _id in enumerate(person_ids):
        print('\r condition2person {}/{}'.format(_i + 1, num_persons), end='')
        all_paths = MetaPaths['籍贯'].get_all_paths_by_node_id(_id)
        for _path in all_paths:
            if GRAPH_DAO.get_node_label_by_id(_path[-2]) == NodeLabels['address']:
                address2person_ids[_path[-2]].add(_id)
        all_paths = MetaPaths['官职'].get_all_paths_by_node_id(_id)
        for _path in all_paths:
            for i, word_id in enumerate(_path):
                if i % 2 == 0:
                    if GRAPH_DAO.get_node_label_by_id(word_id) == NodeLabels['post_type']:
                        post_type2person_ids[word_id].add(_id)
                    if GRAPH_DAO.get_node_label_by_id(word_id) == NodeLabels['address']:
                        post_address2person_ids[word_id].add(_id)
                    if GRAPH_DAO.get_node_label_by_id(word_id) == NodeLabels['office']:
                        office2person_ids[word_id].add(_id)
                    if GRAPH_DAO.get_node_label_by_id(word_id) == NodeLabels['office_type']:
                        office_type2person_ids[word_id].add(_id)
        all_paths = MetaPaths['入仕'].get_all_paths_by_node_id(_id)
        for _path in all_paths:
            for i, word_id in enumerate(_path):
                if i % 2 == 0:
                    if GRAPH_DAO.get_node_label_by_id(word_id) == NodeLabels['entry']:
                        entry2person_ids[word_id].add(_id)
                    if GRAPH_DAO.get_node_label_by_id(word_id) == NodeLabels['entry_type']:
                        entry_type2person_ids[word_id].add(_id)
    GRAPH_DAO.close_connect()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE post_type2person_ids
                (
                    post_type_id BIGINT PRIMARY KEY,
                    person_ids TEXT NOT NULL
                );
            ''')
    c.execute('''CREATE TABLE post_address2person_ids
                (
                    post_address_id BIGINT PRIMARY KEY,
                    person_ids TEXT NOT NULL
                );
            ''')
    c.execute('''CREATE TABLE office2person_ids
                (
                    office_id BIGINT PRIMARY KEY,
                    person_ids TEXT NOT NULL
                );
            ''')
    c.execute('''CREATE TABLE office_type2person_ids
                (
                    office_type_id BIGINT PRIMARY KEY,
                    person_ids TEXT NOT NULL
                );
            ''')
    c.execute('''CREATE TABLE entry2person_ids
                (
                    entry_id BIGINT PRIMARY KEY,
                    person_ids TEXT NOT NULL
                );
            ''')
    c.execute('''CREATE TABLE entry_type2person_ids
                (
                    entry_type_id BIGINT PRIMARY KEY,
                    person_ids TEXT NOT NULL
                );
            ''')
    c.execute('''CREATE TABLE address2person_ids
                (
                    address_id BIGINT PRIMARY KEY,
                    person_ids TEXT NOT NULL
                );
            ''')
    for post_type_id, person_ids in post_type2person_ids.items():
        c.execute("INSERT INTO post_type2person_ids VALUES (?,?)", (int(post_type_id), json.dumps(list(person_ids))))
    for address_id, person_ids in post_address2person_ids.items():
        c.execute("INSERT INTO post_address2person_ids VALUES (?,?)", (int(address_id), json.dumps(list(person_ids))))
    for post_id, person_ids in office2person_ids.items():
        c.execute("INSERT INTO office2person_ids VALUES (?,?)", (int(post_id), json.dumps(list(person_ids))))
    for post_id, person_ids in office_type2person_ids.items():
        c.execute("INSERT INTO office_type2person_ids VALUES (?,?)", (int(post_id), json.dumps(list(person_ids))))
    for entry_id, person_ids in entry2person_ids.items():
        c.execute("INSERT INTO entry2person_ids VALUES (?,?)", (int(entry_id), json.dumps(list(person_ids))))
    for entry_type_id, person_ids in entry_type2person_ids.items():
        c.execute("INSERT INTO entry_type2person_ids VALUES (?,?)", (int(entry_type_id), json.dumps(list(person_ids))))
    for address_id, person_ids in address2person_ids.items():
        c.execute("INSERT INTO address2person_ids VALUES (?,?)", (int(address_id), json.dumps(list(person_ids))))
    conn.commit()
    print('condition2person finish')


if __name__ == "__main__":
    # neo4j = Shell('neo4j.bat console', 'Started')
    # neo4j.run_background()
    # whole_g, node2data, rel2data = get_whole_graph()
    sql_dataset = Path('./dataset/graph.db')
    # if sql_dataset.exists():
    #     sql_dataset.unlink()
    # save2sqlite(whole_g, node2data, rel2data, str(sql_dataset))
    # insert_node2person2count(str(sql_dataset))
    # insert_condition2person(str(sql_dataset))
