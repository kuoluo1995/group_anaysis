import json
import sqlite3
import threading
import time
import networkx as nx

from py2neo import Graph

ip = 'bolt://localhost:7687'
username = 'neo4j'
password = '123456'


def get_whole_graph():
    def multiThreadLoad(func, epoch):
        ts = []
        # 44
        for i in range(epoch):
            if i % 10 == 0:
                print(i)
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

            graph.add_edge(n1_id, n2_id, r_id=r_id)
            rel2data[r_id] = (r_type, r_name, '')

    def loadNodes(time, num_per_time=100000):
        query = ''' MATCH (n)
                    RETURN id(n), labels(n), n.name, n.en_name
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
            if n_id in node2data:
                print(node2data[n_id], (n_type, n_name, n_en_name,), n_id, '重复了')
            node2data[n_id] = (n_type, n_name, n_en_name,)

    neo_graph = Graph('bolt://localhost:7687', username='neo4j', password='123456')
    graph = nx.MultiDiGraph()
    node2data = {}
    rel2data = {}
    multiThreadLoad(loadEdges, 3)
    multiThreadLoad(loadNodes, 3)
    # multiThreadLoad(loadEdges, 55)
    # multiThreadLoad(loadNodes, 14)
    print(graph.number_of_nodes(), graph.number_of_edges(), len(node2data))
    return graph, node2data, rel2data


def save2sqlite(graph, node2data, rel2data, db_path):
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
    c.execute('''CREATE INDEX node_label_index ON node2data (label)''')
    c.execute('''CREATE INDEX rel_label_index ON rel2data (label)''')

    for source, target, key in graph.edges(keys=True):
        data = graph[source][target][key]
        r_id = data['r_id']
        c.execute("INSERT INTO graph VALUES (?,?,?,?)", (source, target, r_id, json.dumps({})))

    for _id in node2data:
        label, name, en_name = node2data[_id]
        c.execute("INSERT INTO node2data VALUES (?,?,?,?,?)", (_id, label, name, en_name, json.dumps({})))

    for _id in rel2data:
        label, name, en_name = rel2data[_id]
        c.execute("INSERT INTO rel2data VALUES (?,?,?,?,?)", (_id, label, name, en_name, json.dumps({})))
    conn.commit()

    print('graph is save')


if __name__ == "__main__":
    whole_g, node2data, rel2data = get_whole_graph()
    save2sqlite(whole_g, node2data, rel2data, './graph.db')
