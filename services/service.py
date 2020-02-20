from utils.common_util import sort_dict, Label
from utils.sqlite_graph_util import get_node_id_by_name, get_sub_graph, get_node_label_by_id, get_relation, \
    get_node_name_by_id


def get_ranges_by_name(name):
    people_id = get_node_id_by_name(name)[0]
    sub_graph = get_sub_graph(people_id, depth=3)
    result = {Label.person: {}, Label.dynasty: {}, Label.year: {}, Label.gender: {}, Label.status: {}}
    for node_id in sub_graph.nodes():
        node_label = get_node_label_by_id(node_id)
        if node_label in result.keys():
            result[node_label].update({node_id: get_node_name_by_id(node_id)})
    return result


def get_person_by_ranges(dynastie_id, year_ids, gender_id, statu_id):
    sub_graph = get_sub_graph(dynastie_id, depth=3)
    result = {Label.person: {}}
    min_year = int(get_node_name_by_id(year_ids[0]))
    max_year = int(get_node_name_by_id(year_ids[1]))
    for node_id in sub_graph.nodes():
        node_label = get_node_label_by_id(node_id)
        if node_label == Label.person:
            result[node_label].update({node_id: get_node_name_by_id(node_id)})
            # _year = int(get_node_name_by_id(node_id))
            # if min_year <= _year and _year <= max_year:
            #     pass
    return result


def get_topic_by_ranges():
    return {}
