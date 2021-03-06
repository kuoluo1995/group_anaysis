import json
import os
import timeit
import matplotlib.pyplot as plt
import numpy as np

from services import common
from services.service import get_relation_person_by_name, get_topics_by_person_ids, get_init_ranges, get_person_by_ranges,get_address_by_address_ids, get_all_similar_person, add_topic_weights, get_similar_person, get_compared_topics_by_person_ids
from services.tools.person_tool import get_person_all_dict
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
    EdgeLabels = common.EdgeLabels
    MetaPaths = common.MetaPaths

    GRAPH_DAO.start_connect()
    # dynasties, status, address = get_init_ranges()
    #
    # start = timeit.default_timer()
    # dynastie_id = 716  # 明朝
    # person = get_person_by_ranges([dynastie_id], None, None, None, None, list(address.keys())[:30])
    # print('查询范围内的所有人耗时:{}'.format(timeit.default_timer() - start))
    # CBDB_DAO = common.CBDB_DAO
    # CBDB_DAO.start_connect()
    # person_dict = get_person_all_dict([_id for _id, values in person.items()])
    # person_dict = {key: values for key, values in person_dict.items() if 633615 in values.keys()}
    # person_ids = [_id for _id, values in person.items()][:30]


    start = timeit.default_timer()
    ranges = {'关系': {NodeLabels['association']: 0}, '亲属': {EdgeLabels['kin']: 1}}
    person1 = get_relation_person_by_name('王安石', ranges)
    person2 = get_relation_person_by_name('苏轼', ranges)

    print('查询耗时:{}'.format(timeit.default_timer() - start))
    person_ids1 = [_person_id for _person_id, types in person1.items()]
    person_ids2 = [_person_id for _person_id, types in person2.items()]
    all_person_ids = list(set(person_ids1 + person_ids2))

    print('查询的人:{}'.format(all_person_ids))
    start = timeit.default_timer()
    all_topic_ids, topic_id2sentence_id2position1d, topic_pmi, person_id2position2d, node_dict, edge_dict, topic_id2lrs, all_sentence_dict, topic_id2sentence_ids2vector, person_id2sentence_ids = get_compared_topics_by_person_ids(person_ids1, person_ids2, populate_ratio=0.3, max_topic=10)
    print(len(all_topic_ids))


    # print('查询所有topic的相关性:{}'.format(timeit.default_timer() - start))

    # similar_person = get_similar_person(person_ids, topic_id2lrs)
    # address_ids = [_id for _id, _item in node_dict.items() if _item['label'] == NodeLabels['address']]
    # start = timeit.default_timer()
    # address = get_address_by_address_ids(address_ids)
    # print('查询地址耗时:{}'.format(timeit.default_timer() - start))

    # topic_weights = {'1 2 3': 2}
    # person_id2position2d2, person_dict = add_topic_weights(topic_weights, topic_id2sentence_ids2vector,
    #                                                        person_id2sentence_ids)

    # topic 相似矩阵
    # pmi_names = list()
    # _len = len(topic_pmi)
    # _matrix = np.zeros((_len, _len))
    # for i, x_ids in enumerate(topic_pmi):
    #     topic_names = list()
    #     for t_id in x_ids:
    #         topic_names.append(node_dict[t_id]['name'])
    #     pmi_names.append(' '.join(topic_names))
    #     for j, y_ids in enumerate(topic_pmi):
    #         _matrix[i][j] = topic_pmi[x_ids][y_ids]
    # plt.matshow(_matrix)
    # plt.xticks(list(range(_len)), pmi_names)
    # plt.yticks(list(range(_len)), pmi_names)
    # plt.show()
    # # topic散点图
    # for _topic_id, _sentences_id2position1d in topic_id2sentence_id2position1d.items():
    #     num_sentence = len(_sentences_id2position1d.keys())
    #     colors = np.random.random(num_sentence)
    #     position1d = np.zeros((num_sentence, 2))
    #     position2ds = np.array([_pos1d for _, _pos1d in _sentences_id2position1d.items()])
    #     plt.scatter(position2ds[:, 0], position2ds[:, 1], alpha=0.5, c=colors)
    #     for _sentence_id, _pos1d in _sentences_id2position1d.items():
    #         sentence = list()  # 描述
    #         for i, _id in enumerate(_sentence_id):
    #             if i % 2 == 0:
    #                 sentence.append(node_dict[_id]['name'])
    #             else:
    #                 sentence.append(edge_dict[_id]['name'])
    #         plt.text(_pos1d[0], _pos1d[1], ' '.join(sentence), fontsize=5)
    #     plt.show()

    # 人物散点图
    # num_person = len(person_id2position2d.keys())
    # colors = np.random.random(num_person)
    # position2ds = np.array([_position2d for person_id, _position2d in person_id2position2d.items()])
    # plt.scatter(position2ds[:, 0], position2ds[:, 1], alpha=0.5, c=colors)
    # for _person_id, _pos2d in person_id2position2d.items():
    #     _name = node_dict[_person_id]['name']
    #     plt.text(_pos2d[0], _pos2d[1], _name, fontsize=5)
    # plt.show()

    # 将算法的结果保存成json串，用于提供给前端快速测试
    # input_file = 'input.json'  # 输入的json
    # with open(input_file, 'w') as file_obj:
    #     json.dump(person_ids, file_obj)
    # output_file = 'topic.json'  # 输出的json
    # with open(output_file, 'w') as file_obj:
    #     json.dump(temp, file_obj)
