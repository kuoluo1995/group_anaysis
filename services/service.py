from services.common import Labels


def get_ranges_by_name(name):
    global sqlite_graph
    person_id = sqlite_graph.get_node_id_by_name(name)
    sub_graph = sqlite_graph.get_sub_graph(person_id, depth=2)
    result = {Labels.person: {}, Labels.dynasty: {}, Labels.year: {}, Labels.gender: {}, Labels.status: {}}
    for node_id in sub_graph.nodes():
        node_label = sqlite_graph.get_node_label_by_id(node_id)
        if node_label in result.keys():
            result[node_label].update({node_id: sqlite_graph.get_node_name_by_id(node_id)})
    return result


# todo 还没检测
def get_person_by_ranges(dynastie_id, year_ids, gender_id, statu_id):
    global sqlite_graph
    sub_graph = sqlite_graph.get_sub_graph(dynastie_id, depth=1)
    all_person = set()
    # 根据年代，找到所有的人
    for node_id in sub_graph.nodes():
        node_label = sqlite_graph.get_node_label_by_id(node_id)
        if node_label == Labels.person:
            all_person.add(node_id)
    # 根据年代，性别和社会区分赛选
    person_ids = set()
    min_year = int(sqlite_graph.get_node_name_by_id(year_ids[0]))
    max_year = int(sqlite_graph.get_node_name_by_id(year_ids[1]))
    for _id in all_person:
        person_graph = sqlite_graph.get_sub_graph(_id, depth=1)
        checked = True
        for node_id in person_graph.nodes():
            node_label = sqlite_graph.get_node_label_by_id(node_id)
            if node_label == Labels.year:
                _year = int(sqlite_graph.get_node_name_by_id(node_id))
                if _year < min_year or max_year < _year:
                    checked = False
                    break
            if node_label == Labels.gender:
                if node_id != gender_id:
                    checked = False
                    break
            if node_label == Labels.status:
                if node_id != statu_id:
                    checked = False
                    break
        if checked:
            person_ids.add(_id)
    # 再来筛选topic
    return person_ids


def get_topics_by_person_ids(person_ids):
    person_graph = {_id: sqlite_graph.get_sub_graph(_id) for _id in person_ids}
    for _id in person_ids:
        pass

    # 得到所有先关结点
    all_related_nodes = {_graph.nodes() for _, _graph in person_graph.items()}

    pass
