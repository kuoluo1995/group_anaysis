import math

from services import common
from services.tools import person_tool


def lrs(topic_id, person_ids, smooth=0.01):
    '''似然率统计量(LRS)，表示topic在群体中和总体中的区分度

    :param topic_id: int
    :param person_ids: list(int)
    :return:
    '''
    m_z = len(person_ids) / common.NUM_ALL_PERSON
    m_f = 1 - m_z

    has_topic_person_ids = person_tool.get_person_ids_by_topic_id(topic_id)
    has_topic_person_ids_len = len(has_topic_person_ids)
    if has_topic_person_ids_len == 0:
        return smooth
    m_gz = len([_id for _id in person_ids if _id in has_topic_person_ids]) / has_topic_person_ids_len
    m_gf = 1 - m_gz
    if m_gz == 0 or m_z == 0 or m_f == 0 or m_gf == 0:
        return smooth
    return 2 * (m_gz * math.log(m_gz / m_z) + m_gf * math.log(m_gf / m_f)) * has_topic_person_ids_len
