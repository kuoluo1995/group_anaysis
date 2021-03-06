import json
import timeit
import matplotlib.pyplot as plt
import numpy as np

from services import common
from services.service import get_relation_person_by_name, get_topics_by_person_ids, get_init_ranges, \
    get_person_by_ranges, \
    get_address_by_address_ids, get_all_similar_person, add_topic_weights, get_similar_person, \
    get_top_topic_by_sentence_ids, get_compared_topics_by_person_ids
from services.tools.person_tool import get_person_all_dict
from tools import json_utils
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
    CBDB_DAO = common.CBDB_DAO
    NodeLabels = common.NodeLabels
    EdgeLabels = common.EdgeLabels
    MetaPaths = common.MetaPaths
    # GRAPH_DAO.start_connect()
    # if '韩侂冑' == '韩侂胄':
    #     print()
    # ids = GRAPH_DAO.get_node_ids_by_name('Zhao Ruyu')
    # dynastie_id = GRAPH_DAO.get_node_ids_by_name('Song', node_label=NodeLabels['dynasty'])[0]
    # target_id = []
    # for id in ids:
    #     name = GRAPH_DAO.get_node_name_by_id(id)
    #     all_paths = MetaPaths['朝代'].get_all_paths_by_node_id(id)
    #     for _path in all_paths:
    #         for _i, _word in enumerate(_path):
    #             if _i % 2 == 0 and _word == dynastie_id:
    #                 target_id.append(id)
    # GRAPH_DAO.close_connect()
    # 初始化部分
    # dynasties, status, address, post_type, post_address, office, office_types, entry, entry_type = get_init_ranges()
    # 条件查询人群
    # start = timeit.default_timer()
    # dynastie_ids = [_id for _id, items in dynasties.items() if items['name'] == '宋']
    # GRAPH_DAO.start_connect()
    # address_codes = [GRAPH_DAO.get_node_code_by_id(_id) for _id, items in address.items() if items['name'] == '眉山']
    # GRAPH_DAO.close_connect()
    # CBDB_DAO.start_connect()
    # ids = CBDB_DAO.get_address_by_address_codes(address_codes)
    # CBDB_DAO.close_connect()
    # person = get_person_by_ranges(dynastie_ids, None, None, None, None, address_ids, None, None, None,
    #                               None, None, None)
    print()
    # person_ids = [_id for _id, items in person.items()]
    # print(len(person))
    # person = get_person_by_ranges([dynastie_id], None, None, None, None, None,
    #                               list(post_type.keys())[:1], None, None, None, None, None)
    # print(len(person))
    # person = get_person_by_ranges([dynastie_id], None, None, None, None, None,
    #                               None, list(post_address.keys())[:30], None, None, None, None)
    # print(len(person))
    # person = get_person_by_ranges([dynastie_id], None, None, None, None, None,
    #                               None, None, list(office.keys())[:1000], None, None, None)
    # print(len(person))
    # person = get_person_by_ranges([dynastie_id], None, None, None, None, None,
    #                               None, None, None, list(office_types.keys())[:30], None, None)
    # print(len(person))
    # person = get_person_by_ranges([dynastie_id], None, None, None, None, None,
    #                               None, None, None, None, list(entry.keys())[:30], None)
    # print(len(person))
    # person = get_person_by_ranges([dynastie_id], None, None, None, None, None,
    #                               None, None, None, None, None, list(entry_type.keys())[:30])
    # print(len(person))
    # print('查询范围内的所有人耗时:{}'.format(timeit.default_timer() - start))
    # 通过名字查询
    start = timeit.default_timer()
    ranges = {'关系': {NodeLabels['association']: 0}, '亲属': {EdgeLabels['kin']: 1}}
    person = get_relation_person_by_name('Zhao Ruyu', ranges)
    # print(person)
    print('查询王安石耗时:{}'.format(timeit.default_timer() - start))
    # 查询topic通过 person_ids
    # start = timeit.default_timer()
    # _json = json_utils.load_json('error_search_topic_2020-04-16-14_05_58.427338')
    # person_ids = _json['person_ids[]']
    # person_ids = [int(_id) for _id in person_ids]
    person_ids = [4921, 50879, 50876]
    # populate_ratio = float(_json['populate_ratio'])
    populate_ratio = 0.3
    # max_topic = int(_json['max_topic'])
    max_topic = 10
    all_topic_ids, topic_id2sentence_id2position1d, topic_pmi, person_id2position2d, node_dict, edge_dict, topic_id2lrs, all_sentence_dict, topic_id2sentence_ids2vector, person_id2sentence_ids = get_topics_by_person_ids(
        person_ids, populate_ratio=0.3, max_topic=10)
    print(len(all_topic_ids))
    # 查询相似的人
    # similar_person = get_similar_person(person_ids, topic_id2lrs)
    # 查询地址
    # address_ids = [_id for _id, _item in node_dict.items() if _item['label'] == NodeLabels['address']]
    # start = timeit.default_timer()
    # address = get_address_by_address_ids(address_ids)
    # print('查询地址耗时:{}'.format(timeit.default_timer() - start))
    # 条件topic
    # _json = json_utils.load_json('error_adjust_topic_weights_2020-04-18-18_18_14.142410')
    # topic_weights = _json['topic_weights']
    # topic_weights = {tuple([int(_id) for _id in _topic_id.split(' ')]): _weight for _topic_id, _weight in
    #                  topic_weights.items()}
    # _data = json_utils.load_json(_json['adjust_topic_weights_params'])
    # topic_id2sentence_ids2vector_json = {}
    # for _topic_id, _items in _data['topic_id2sentence_ids2vector'].items():
    #     _topic_id = tuple([int(_id) for _id in _topic_id.split(' ')])
    #     topic_id2sentence_ids2vector_json[_topic_id] = {}
    #     for _sentence_id, _value in _items.items():
    #         _sentence = tuple([int(_id) for _id in _sentence_id.split(' ')])
    #         topic_id2sentence_ids2vector_json[_topic_id][_sentence] = [float(_v) for _v in _value]
    # person_id2sentence_ids = {int(_person_id): [tuple(_sentence_id) for _sentence_id in _sentence_ids] for
    #                           _person_id, _sentence_ids in _data['person_id2sentence_ids'].items()}
    # person_id2position2d2, person_dict = add_topic_weights(topic_weights, topic_id2sentence_ids2vector_json,
    #                                                        person_id2sentence_ids)
    # 对比topic
    person_ids1 = [4921, 15378, 15379, 43374, 48805, 50876, 50879]
    person_ids2 = [15378, 15379, 43374, 48805]
    start = timeit.default_timer()
    all_topic_ids, topic_id2sentence_id2position1d, topic_pmi, person_id2position2d, node_dict, edge_dict, topic_id2lrs, all_sentence_dict, topic_id2sentence_ids2vector, person_id2sentence_ids = get_compared_topics_by_person_ids(
        person_ids1, person_ids2, populate_ratio=0.3, max_topic=10)
    print(len(all_topic_ids))
    # # topic 相似矩阵
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
    #
    # # 人物散点图
    # num_person = len(person_id2position2d.keys())
    # colors = np.random.random(num_person)
    # position2ds = np.array([_position2d for person_id, _position2d in person_id2position2d.items()])
    # plt.scatter(position2ds[:, 0], position2ds[:, 1], alpha=0.5, c=colors)
    # for _person_id, _pos2d in person_id2position2d.items():
    #     _name = node_dict[_person_id]['name']
    #     plt.text(_pos2d[0], _pos2d[1], _name, fontsize=5)
    # plt.show()
    #
    # # 将算法的结果保存成json串，用于提供给前端快速测试
    # # input_file = 'input.json'  # 输入的json
    # # with open(input_file, 'w') as file_obj:
    # #     json.dump(person_ids, file_obj)
    # # output_file = 'topic.json'  # 输出的json
    # # with open(output_file, 'w') as file_obj:
    # #     json.dump(temp, file_obj)
