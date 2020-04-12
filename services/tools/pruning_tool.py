import math

from services import common
from services.tools import person_tool
from collections import defaultdict
import numpy as np
from tools.sort_utils import lda

def getTopicWeights(topic_ids, person_ids):
    person_ids = set(person_ids)
    all_person_ids = set()
    person2topics = defaultdict(set)
    for t in topic_ids:
        has_t_pids = person_tool.get_person_ids_by_topic_id(t)
        # all_person_ids += has_t_pids
        for p in has_t_pids:
            all_person_ids.add(p)
            person2topics[p].add(t)

    all_person_ids = list(all_person_ids)

    def getVec(pid):
        return tuple([1 if t in person2topics[pid] else -1 for t in topic_ids])

    # vec2label = {}
    # for p in all_person_ids:
    #     vec = getVec(p)
    #     label = 1 if p in person_ids else 2
    #     if vec in vec2label and vec2label[vec] == 1:
    #         continue
    #     vec2label[vec] = label
    # vecs = [list(vec) for vec in vec2label.keys()]
    # labels = [label for label in vec2label.values()]
    # print(vecs)
    vecs = [getVec(p) for p in all_person_ids]
    labels = [1 if p in all_person_ids else 2 for p in all_person_ids]
    # print(len(all_person_ids), len(person_ids))

    # for p in labels:
    #     if p == 1:
    #         print(1111)
    #         exit()
    # print(vecs, labels)
    # for vec in vecs:
    #     # print(vec)
    #     if vec[1] == 1:
    #         print(vec)
            # exit()
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    lda_model = LinearDiscriminantAnalysis(n_components=1)
    lda_model.fit(vecs, labels)
    # # new_vec = 
    # # fit_transform(vecs, labels)
    # # w = new_vec / np.array(vecs)
    w = lda_model.coef_[0]
    w -= np.min(w)
    w += 1
    # print()
    # new_vec, w = lda(vecs, labels, 1)
    topic2w = {t: w[i] for i, t in enumerate(topic_ids)}
    return topic2w

def compared_lrs(topic_id, person_ids1, person_ids2, smooth = 0.01):
    '''似然率统计量(LRS)，表示topic在群体中和总体中的区分度

    :param topic_id: int
    :param person_ids: list(int)
    :return:
    '''
    all_person_ids = set(person_ids1 + person_ids2)
    person_ids1 = set(person_ids1)
    person_ids2 = set(person_ids2)
    

    z_person_ids = set([pid for pid in person_ids1 if pid not in person_ids2])

    # m_z肯定很小
    m_z = len(z_person_ids) / len(all_person_ids)
    m_f = 1 - m_z

    
    has_topic_person_ids = person_tool.get_person_ids_by_topic_id(topic_id)  #规则覆盖的
    has_topic_person_ids = [pid for pid in has_topic_person_ids if pid in all_person_ids]

    has_topic_person_ids_len = len(has_topic_person_ids)
    if has_topic_person_ids_len == 0:
        return smooth
    m_gz = len([_id for _id in z_person_ids if _id in has_topic_person_ids]) / has_topic_person_ids_len
    m_gf = 1 - m_gz

    if m_gz == 0 or m_z == 0 or m_f == 0 or m_gf == 0:
        return smooth

    lrs_value = 2 * (m_gz * math.log(m_gz / m_z) + m_gf * math.log(m_gf / m_f))
    GRAPH_DAO = common.GRAPH_DAO
    topic_name = [GRAPH_DAO.get_node_name_by_id(elm) for elm in topic_id]
    print(topic_name,  lrs_value)
    return lrs_value


def lrs(topic_id, person_ids, smooth=0.01):
    '''似然率统计量(LRS)，表示topic在群体中和总体中的区分度

    :param topic_id: int
    :param person_ids: list(int)
    :return:
    '''

    # m_z肯定很小
    m_z = len(person_ids) / common.NUM_ALL_PERSON
    m_f = 1 - m_z

    
    has_topic_person_ids = person_tool.get_person_ids_by_topic_id(topic_id)  #规则覆盖的
    has_topic_person_ids_len = len(has_topic_person_ids)
    if has_topic_person_ids_len == 0:
        return smooth
    m_gz = len([_id for _id in person_ids if _id in has_topic_person_ids]) / has_topic_person_ids_len
    m_gf = 1 - m_gz

    # print(topic_id, topic_name, m_z, m_gz)
    if m_gz == 0 or m_z == 0 or m_f == 0 or m_gf == 0:
        return smooth
        #  * has_topic_person_ids_len
    lrs_value = 2 * (m_gz * math.log(m_gz / m_z) + m_gf * math.log(m_gf / m_f))
    # FOIL
    # lrs_value = m_gz * has_topic_person_ids_len * (math.log(m_gz / m_z) - math.log(m_z / m_z))
    # GRAPH_DAO = common.GRAPH_DAO
    # topic_name = [GRAPH_DAO.get_node_name_by_id(elm) for elm in topic_id]
    # print(topic_name, m_z, math.log(m_gz / m_z), m_gz, math.log(m_gf / m_f), lrs_value)
    return lrs_value
