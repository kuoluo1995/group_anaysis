import sqlite3
import networkx as nx

db_path = './dataset/graph.db'
sqlite_graph = sqlite3.connect(db_path)
sql_cursor = sqlite_graph.cursor()
use_cache = True

node_name2id_cache = {}


def get_node_id_by_name(node_name):
    global node_name2id_cache
    if node_name not in node_name2id_cache:
        rows = sql_cursor.execute('''SELECT id FROM node2data WHERE name = ?''', (node_name,))
        rows = [row[0] for row in rows]
        if not use_cache:
            return rows
        node_name2id_cache[node_name] = rows
    # if len(rows) == 0:
    #     raise Exception(node_name, '没有对应的name')
    return list(node_name2id_cache[node_name])


node_id2name_cache = {}
def get_node_name_by_id(node_id):
    global node_id2name_cache
    if node_id not in node_id2name_cache:
        rows = sql_cursor.execute('''SELECT name FROM node2data WHERE id = ?''', (node_id,))
        rows = list(rows)
        if not use_cache:
            return str(rows[0][0])
        # if len(rows) == 0:
        #     raise Exception(node_id, '没有对应的name')
        node_id2name_cache[node_id] = str(rows[0][0])
    return node_id2name_cache[node_id]


node_id2label_cache = {}


def get_node_label_by_id(node_id):
    global node_id2label_cache
    if node_id not in node_id2label_cache:
        rows = sql_cursor.execute('''SELECT label FROM node2data WHERE id = ?''', (node_id,))
        rows = list(rows)
        if not use_cache:
            return str(rows[0][0])
        # if len(rows) == 0:
        #     raise Exception(node_id, '没有对应的label')
        node_id2label_cache[node_id] = str(rows[0][0])
    return node_id2label_cache[node_id]


in_relation_cache = {}


def get_in_relations(target_id):
    global in_relation_cache
    if target_id not in in_relation_cache:
        rows = sql_cursor.execute('''SELECT source, r_id FROM graph WHERE target = ?''', (target_id,))
        rows = [(row[0], target_id, row[1]) for row in rows]
        if not use_cache:
            return rows
        in_relation_cache[target_id] = rows
    return list(in_relation_cache[target_id])


out_relation_cache = {}


def get_out_relations(source_id):
    global out_relation_cache
    if source_id not in out_relation_cache:
        rows = sql_cursor.execute('''SELECT  target, r_id FROM graph WHERE source = ?''', (source_id,))
        rows = [(source_id, row[0], row[1]) for row in rows]
        if not use_cache:
            return rows
        out_relation_cache[source_id] = rows
    # source, target, r_id
    return list(out_relation_cache[source_id])


def get_relation(node_id):
    # print(node_id,  getInRels(node_id), getOutRels(node_id))
    return get_in_relations(node_id) + get_out_relations(node_id)


def get_out_nodes(node_id):
    return [target for source, target, r_id in get_out_relations(node_id)]


# 还需要清理下边， 我猜我这个subg有问题
def get_sub_graph(node_id, depth=3):
    # print(node_id, '提取子图')
    pop_nodes = set([node_id])
    used_nodes = set()

    node2depth = {node_id: 0}
    while len(pop_nodes) != 0:
        now_node = pop_nodes.pop()
        used_nodes.add(now_node)
        next_depth = node2depth[now_node] + 1

        nei_nodes = get_out_nodes(now_node)
        for nei_node in nei_nodes:
            if nei_node not in used_nodes and nei_node not in pop_nodes and next_depth < depth:
                pop_nodes.add(nei_node)
                node2depth[nei_node] = next_depth
            elif nei_node in node2depth and node2depth[nei_node] > next_depth:
                node2depth[nei_node] = next_depth
                if next_depth < depth and nei_node in used_nodes:
                    pop_nodes.add(nei_node)
                    used_nodes.remove(nei_node)

    sub_graph = nx.MultiDiGraph()
    for node in used_nodes:
        for source, target, r_id in get_out_relations(node):
            if target in used_nodes:
                sub_graph.add_edge(source, target, r_id=r_id)
    return sub_graph
