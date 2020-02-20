from utils.common_util import sort_dict, Labels
from utils.sqlite_graph_util import sqlite_graph


def get_ranges_by_name(name):
    global sqlite_graph
    people_id = sqlite_graph.get_node_id_by_name(name)
    sub_graph = sqlite_graph.get_sub_graph(people_id)
    result = {Labels.person: {}, Labels.dynasty: {}, Labels.year: {}, Labels.gender: {}, Labels.status: {}}
    for node_id in sub_graph.nodes():
        node_label = sqlite_graph.get_node_label_by_id(node_id)
        if node_label in result.keys():
            result[node_label].update({node_id: sqlite_graph.get_node_name_by_id(node_id)})
    return result


def get_person_by_ranges(dynastie_id, year_ids, gender_id, statu_id):
    global sqlite_graph
    sub_graph = sqlite_graph.get_sub_graph(dynastie_id)
    result = {Labels.person: {}}
    min_year = int(sqlite_graph.get_node_name_by_id(year_ids[0]))
    max_year = int(sqlite_graph.get_node_name_by_id(year_ids[1]))
    for node_id in sub_graph.nodes():
        node_label = sqlite_graph.get_node_label_by_id(node_id)
        if node_label == Labels.person:
            result[node_label].update({node_id: sqlite_graph.get_node_name_by_id(node_id)})
            # _year = int(get_node_name_by_id(node_id))
            # if min_year <= _year and _year <= max_year:
            #     pass
    return result


def get_topic_by_ranges():
    return {}
