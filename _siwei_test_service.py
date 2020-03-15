import matplotlib.pyplot as plt
import numpy as np

from services import common
from services.service import get_ranges_by_name, get_topics_by_person_ids, get_init_ranges, get_person_by_ranges, \
    get_address_by_person_ids
from tools.sort_utils import sort_dict2list, intersect
import math
from collections import defaultdict

# linux去除中文乱码
# ch_font =  FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',size=20)
# rcParams['axes.unicode_minus']=False #解决负号'-'显示为方块的问题
# mpl.rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
# Windows去除中文乱码
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
if __name__ == '__main__':
    print('start')
    GRAPH_DAO = common.GRAPH_DAO
    NodeLabels = common.NodeLabels
    GRAPH_DAO.start_connect()

    # GRAPH_DAO.getHasNodePeople(1096388)

    # dynasties, status = get_init_ranges()
    # , NodeLabels['dynasty'], NodeLabels['year'], NodeLabels['gender'], NodeLabels['status']
    labels = [NodeLabels['person']]
    ranges = get_ranges_by_name(labels, '王安石')

    # person = get_person_by_ranges([575], 980, 1120, False, [633480])

    # address = get_address_by_person_ids(person.keys())
    print('range end')
    GRAPH_DAO.start_connect()
    person_id2relation = {_id: len(GRAPH_DAO.get_in_edges(_id) + GRAPH_DAO.get_out_edges(_id)) for _id in ranges[NodeLabels['person']]}
    person_id2relation = sort_dict2list(person_id2relation)[:30]
    person_ids = [_id[0] for _id in person_id2relation]
    

    print('filter end')
    # label2topic_ids 也不需要了
    all_topic_ids, topic_id2sentence_id2position1d, pmi_node, person_id2position2d, node_dict, edge_dict = get_topics_by_person_ids(person_ids)


    def findHasTopic(topic):
        has_topic_pids = None
        for nid in topic:
            temp_pids = GRAPH_DAO.getHasNodePeople(nid)
            if has_topic_pids is None:
                has_topic_pids = temp_pids
                continue
            has_topic_pids = intersect(has_topic_pids, temp_pids)
        return has_topic_pids
    
    # 计算LRS
    def LRS(topic, pids):
        ALL_PEOPLE_NUM = 11813
        m_z = len(pids)/ALL_PEOPLE_NUM
        m_f = 1 - m_z

        has_topic_ps = findHasTopic(topic)
        has_topic_ps_len = len(has_topic_ps)
        # 似乎有问题
        if has_topic_ps_len == 0:
            return 0
        # print(topic, has_topic_ps)
        # 
        m_gz = len([pid for pid in pids if pid in has_topic_ps] )/has_topic_ps_len
        m_gf = 1 - m_gz

        # print(m_z, m_f, m_gz, m_gf)
        return 2 * (m_gz*math.log(m_gz/m_z) + m_gf*math.log(m_gf/m_f)) * has_topic_ps_len

    GRAPH_DAO.start_connect()
    topic2lrs = {}  # siwei: 这个以后也要发给前端
    for topic in all_topic_ids:
        topic2lrs[topic] = LRS(topic, person_ids)
    GRAPH_DAO.close_connect()
  
    # GRAPH_DAO.close_connect()

    # siwei: 找到所有相似的人, 要做成一个接口
    def findAllSimPeople(now_pids, all_topics, topic2lrs, N = 20):
        pid2topic_num = defaultdict(int)
        for topic in all_topics:
            has_topic_pids = findHasTopic(topic)
            for pid in has_topic_pids:
                if pid in now_pids:
                    continue
                pid2topic_num[pid] += topic2lrs[topic]
        return [pid for pid, _ in sort_dict2list(pid2topic_num, N=N)]

    sim_pids = findAllSimPeople(person_ids, all_topic_ids, topic2lrs)

    # todo: 试下svm


    # print(1, [GRAPH_DAO.get_node_name_by_id(pid) for pid in sim_pids])

    # 相似矩阵
    # print(pmi_node)
    # pmi_names = list()
    # _len = len(pmi_node)
    # _matrix = np.zeros((_len, _len))
    # for i, x_id in enumerate(pmi_node):
    #     pmi_names.append(','.join([GRAPH_DAO.get_node_name_by_id(nid) for nid in x_id]))
    #     for j, y_id in enumerate(pmi_node):
    #         _matrix[i][j] = pmi_node[x_id][y_id]
    # plt.matshow(_matrix)
    # plt.xticks(list(range(_len)), pmi_names)
    # plt.yticks(list(range(_len)), pmi_names)
    # plt.show()

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

        # position2d = np.zeros((num_sentence, 2))
        # _index = 0
        # for _, _pos2d in _sentences_id2position1d.items():
        #     position2d[_index] = _pos2d
        #     _index += 1
        # plt.scatter(position2d[:,0], position2d[:,1], alpha=0.5, c=colors)

        for _sentence_id, _pos1d in _sentences_id2position1d.items():
            sentence = ''  # 描述
            for i, _id in enumerate(_sentence_id):
                if i % 3 == 0 or i % 3 == 2:
                    # ' ' + 
                    sentence += node_dict[_id]['name']
                else:
                    # ' ' + 
                    sentence += edge_dict[_id]['name']
            plt.text(0, _pos1d, sentence, fontsize=5)
            # plt.text(_pos1d[0], _pos1d[1], sentence, fontsize=5)
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
