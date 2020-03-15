# 创建topic2person的倒排索引
import numpy as np

from services import common
from services.service import get_topics_by_person_ids
from collections import defaultdict
from services.tools.sentence_topic_tool import get_sentence_ids_dict
import json

GRAPH_DAO = common.GRAPH_DAO

# GRAPH_DAO.start_connect()
# sql_c = GRAPH_DAO.conn.cursor()
# sql_c.execute('''
#     CREATE TABLE reverse_index_person_5
#     (
#         name BIGINT PRIMARY KEY,
#         pids TEXT NOT NULL
#     );
# ''')
# GRAPH_DAO.conn.commit()
# print('创建成功')

word2pids = defaultdict(lambda **arg: defaultdict(int))
# 获得倒排索引


all_pids = GRAPH_DAO.getAllPersons()

GRAPH_DAO.start_connect()
sql_c = GRAPH_DAO.conn.cursor()

for index, pid in enumerate(all_pids):
    if (index+1) % 1000 == 0:
        print(index, len(all_pids))
        # break

    pid2values, _, _ = get_sentence_ids_dict([pid], random_epoch=1000)

    values = pid2values[pid]
    if len(values) < 10:
        continue

    for value in values:
        words = [word for index, word in enumerate(value) if index % 3 != 1]
        words = set(words)
        for word in words:
            word2pids[word][pid] += 1

for word in word2pids:
    sql_c.execute( "INSERT INTO reverse_index_person_5 VALUES (?,?)", (int(word), json.dumps(word2pids[word])))
GRAPH_DAO.conn.commit()

