import timeit

import matplotlib.pyplot as plt
import numpy as np

from services import common
from services.service import get_ranges_by_name, get_topics_by_person_ids, get_person_by_dynastie, \
    delete_person_by_ranges
from utils.sort_utils import sort_dict2list

# linux去除中文乱码
# ch_font =  FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',size=20)
# rcParams['axes.unicode_minus']=False #解决负号'-'显示为方块的问题
# mpl.rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
# Windows去除中文乱码
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
if __name__ == '__main__':
    DAO = common.DAO
    NodeLabels = common.NodeLabels
    ranges = get_ranges_by_name('王安石')
    person_ids = ranges[NodeLabels['person']].keys()
    start = timeit.default_timer()
    all_person = get_person_by_dynastie('宋')
    print('1:{}'.format(timeit.default_timer() - start))
    for _person_id in all_person['person_ids']:
        print({_person_id: DAO.get_node_name_by_id(_person_id)})
    all_person = all_person['person_ids']
    start = timeit.default_timer()
    result = delete_person_by_ranges(all_person, 960, 1127, ['男', '女'], None)
    print('1:{}'.format(timeit.default_timer() - start))
    person_id2relation = {_id: len(common.DAO.get_in_edges(_id) + common.DAO.get_out_edges(_id)) for _id in person_ids}
    person_id2relation = sort_dict2list(person_id2relation)
    person_ids = [_id[0] for _id in person_id2relation]
    temp = get_topics_by_person_ids(person_ids)

    # 相似矩阵
    pmi_node = temp['pmi_node']
    _len = len(pmi_node)
    _matrix = np.zeros((_len, _len))
    for i, _node_x in enumerate(pmi_node):
        for j, _node_y in enumerate(pmi_node):
            _matrix[i][j] = pmi_node[_node_x][_node_y]
    plt.matshow(_matrix)
    plt.xticks(list(range(_len)), pmi_node.keys())
    plt.yticks(list(range(_len)), pmi_node.keys())
    plt.show()

    # topic散点图
    topic2sentence_positions = temp['topic2sentence_positions']
    for _topic, _sentences_position in topic2sentence_positions.items():
        num_sentence = len(_sentences_position.keys())
        colors = np.random.random(num_sentence)
        position_2d = np.zeros(num_sentence)
        _index = 0
        for _sentence, _pos in _sentences_position.items():
            position_2d[_index] = _pos
            _index += 1
        plt.scatter(np.zeros(num_sentence), position_2d, alpha=0.5, c=colors)
        for _sentence, _pos in _sentences_position.items():
            plt.text(0, _pos, _sentence, fontsize=5)
        plt.show()

    # 人物散点图
    person2positions = temp['person2positions']
    num_person = len(person2positions.keys())
    colors = np.random.random(num_person)
    positions = np.array([_position['position'] for person_id, _position in person2positions.items()])
    plt.scatter(positions[:, 0], positions[:, 1], alpha=0.5, c=colors)
    for _person_id, _items in person2positions.items():
        _name = _items['name']
        _position = _items['position']
        plt.text(_position[0], _position[1], _name, fontsize=5)
    plt.show()

    # 将算法的结果保存成json串，用于提供给前端快速测试
    # input_file = 'input.json'  # 输入的json
    # with open(input_file, 'w') as file_obj:
    #     json.dump(person_ids, file_obj)
    # output_file = 'topic.json'  # 输出的json
    # with open(output_file, 'w') as file_obj:
    #     json.dump(temp, file_obj)
