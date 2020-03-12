import timeit

import matplotlib.pyplot as plt
import numpy as np

from services import common
from services.service import get_ranges_by_name, get_topics_by_person_ids, get_init_ranges, get_person_by_ranges, \
    get_address_by_person_ids
from tools.sort_utils import sort_dict2list

# linux去除中文乱码
# ch_font =  FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',size=20)
# rcParams['axes.unicode_minus']=False #解决负号'-'显示为方块的问题
# mpl.rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
# Windows去除中文乱码
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
if __name__ == '__main__':
    GRAPH_DAO = common.GRAPH_DAO
    NodeLabels = common.NodeLabels

    dynasties, status = get_init_ranges()

    labels = [NodeLabels['person'], NodeLabels['dynasty'], NodeLabels['year'], NodeLabels['gender'],
              NodeLabels['status']]
    start = timeit.default_timer()
    ranges = get_ranges_by_name(labels, '王安石')
    print('查询王安石耗时:{}'.format(timeit.default_timer() - start))
    start = timeit.default_timer()
    person = get_person_by_ranges([575], 980, 1120, False, [633480])
    print('查询范围内的所有人耗时:{}'.format(timeit.default_timer() - start))
    start = timeit.default_timer()
    address = get_address_by_person_ids(person.keys())
    print('查询地址耗时:{}'.format(timeit.default_timer() - start))
    GRAPH_DAO.start_connect()
    start = timeit.default_timer()
    person_id2relation = {_id: len(GRAPH_DAO.get_in_edges(_id) + GRAPH_DAO.get_out_edges(_id)) for _id in
                          ranges[NodeLabels['person']]}
    print('查询所有人的相关性:{}'.format(timeit.default_timer() - start))
    GRAPH_DAO.close_connect()
    person_id2relation = sort_dict2list(person_id2relation)[:15]
    person_ids = [_id[0] for _id in person_id2relation]
    start = timeit.default_timer()
    all_topic_ids, label2topic_ids, topic_id2sentence_id2position1d, pmi_node, person_id2position2d, node_dict, edge_dict = get_topics_by_person_ids(
        person_ids)
    print('查询所有topic的相关性:{}'.format(timeit.default_timer() - start))
    # 相似矩阵
    pmi_names = list()
    _len = len(pmi_node)
    _matrix = np.zeros((_len, _len))
    for i, x_id in enumerate(pmi_node):
        pmi_names.append(node_dict[x_id])
        for j, y_id in enumerate(pmi_node):
            _matrix[i][j] = pmi_node[x_id][y_id]
    plt.matshow(_matrix)
    plt.xticks(list(range(_len)), pmi_names)
    plt.yticks(list(range(_len)), pmi_names)
    plt.show()

    # topic散点图
    for _topic_id, _sentences_id2position1d in topic_id2sentence_id2position1d.items():
        num_sentence = len(_sentences_id2position1d.keys())
        colors = np.random.random(num_sentence)
        position1d = np.zeros(num_sentence)
        _index = 0
        for _, _pos1d in _sentences_id2position1d.items():
            position1d[_index] = _pos1d
            _index += 1
        plt.scatter(np.zeros(num_sentence), position1d, alpha=0.5, c=colors)
        for _sentence_id, _pos1d in _sentences_id2position1d.items():
            sentence = ''  # 描述
            for i, _id in enumerate(_sentence_id):
                if i % 3 == 0 or i % 3 == 2:
                    sentence += ' ' + node_dict[_id]['name']
                else:
                    sentence += ' ' + edge_dict[_id]['name']
            plt.text(0, _pos1d, sentence, fontsize=5)
        plt.show()

    # 人物散点图
    num_person = len(person_id2position2d.keys())
    colors = np.random.random(num_person)
    position2ds = np.array([_position2d for person_id, _position2d in person_id2position2d.items()])
    plt.scatter(position2ds[:, 0], position2ds[:, 1], alpha=0.5, c=colors)
    for _person_id, _pos2d in person_id2position2d.items():
        _name = node_dict[_person_id]['name']
        plt.text(_pos2d[0], _pos2d[1], _name, fontsize=5)
    plt.show()

    # 将算法的结果保存成json串，用于提供给前端快速测试
    # input_file = 'input.json'  # 输入的json
    # with open(input_file, 'w') as file_obj:
    #     json.dump(person_ids, file_obj)
    # output_file = 'topic.json'  # 输出的json
    # with open(output_file, 'w') as file_obj:
    #     json.dump(temp, file_obj)
