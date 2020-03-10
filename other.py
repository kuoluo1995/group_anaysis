# -*- coding: utf-8 -*-
from py2neo import Graph, Node, Relationship, cypher, NodeMatcher
import networkx as nx
import threading
import time
import math
import sqlite3
import json
import random
import copy

from services import common
from tools.sort_utils import sort_dict2list

GRAPH_DAO = common.GRAPH_DAO
NodeLabels = common.NodeLabels
attrs = common.MetaPaths

c_p = '王安石'
c_p_id = GRAPH_DAO.get_node_ids_by_name(c_p)
c_p_id = c_p_id[0]
c_subg = GRAPH_DAO.getSubGraph(c_p_id, depth=3)
c_subg2 = GRAPH_DAO.get_sub_graph(c_p_id, max_depth=3)
print('start')
c_subg = GRAPH_DAO.getSubGraph(c_p_id, depth=3)
c_subg2 = GRAPH_DAO.get_sub_graph(c_p_id, max_depth=3)

info_people = [node_id for node_id in c_subg.nodes() if GRAPH_DAO.get_node_label_by_id(node_id) == 'Person']
info_people2 = [node_id for node_id in c_subg2.nodes() if GRAPH_DAO.get_node_label_by_id(node_id) == 'Person']
info_people2rel_len = {
    p: len(GRAPH_DAO.get_in_edges(p) + GRAPH_DAO.get_out_edges(p))
    for p in info_people
}

info_people = sort_dict2list(info_people2rel_len)[:30]
info_people = [GRAPH_DAO.get_node_name_by_id(item[0]) for item in info_people]
print(info_people)

# info_people = ["贺铸","周邦彦","李清照","陆游","周邦彦","李清照","陆游","辛弃疾","姜夔","黄庭坚","赵明诚"]
# # # ["晏殊","苏轼","黄庭坚","晏几道","秦观",

# def getPersonIds(person_names):
#     id2person = {}
#     name2pid = {}
#     for pname in info_people:
#         pid = getIdByName(pname)[0]
#         id2person[pid] = pname
#         name2pid[pname] = pid
#     return id2person, name2pid
#
#
# pid2person, name2pid = getPersonIds(info_people)
# info_people_ids = list(pid2person.keys())
# # print(pid2person)
#
# # # 找到相似路径
# #     # 属性
# print('start')
# id2p_subg = {id: getSubGraph(id) for id in pid2person}
# id2p_subg_tree = {p_id: nx.bfs_tree(subg, p_id) for p_id, subg in id2p_subg.items()}
# print('子图提取完毕')
#
# # 计算节点的支持度,可以用作转移概率
# # 定义一个相关度，近的且支持度高的不加一， 1/最短距离
#
# all_related_nodes = []
# for p_id, subg in id2p_subg.items():
#     all_related_nodes += subg.nodes()
# all_related_nodes = set(all_related_nodes)
# print('相关节点数量', len(all_related_nodes))
#
# node2sup = {}
# node2relevancy = {}
# node_name2node_id = {}
# for rel_node in all_related_nodes:
#     # print(rel_node)
#     Cyx = 0  # count(y,x)
#     Ryx = 0  # 相关度数
#     for p_id, subg in id2p_subg.items():
#         subg_tree = id2p_subg_tree[p_id]
#         if rel_node in subg:
#             Cyx += 1
#
#             depth = nx.shortest_path_length(subg_tree, p_id, rel_node)
#             Ryx += 1 / math.log(depth + 2)
#
#     node_name = getNodeName(rel_node)
#     node_name2node_id[node_name] = rel_node
#     if node_name not in node2relevancy:
#         node2relevancy[node_name] = 0
#     node2relevancy[node_name] = Ryx
#
#     if node_name not in node2sup:
#         node2sup[node_name] = 0
#     node2sup[node_name] += Cyx  # /len(id2p_subg.keys())
# # print(node2relevancy)
# print('相关度计算完毕')
#
#
# def getPid2values(pids):
#     pid2values = {}
#     value2attr = {}
#     value2pid = {}
#     all_values = set()
#     for pid in pids:
#         values = set()
#         for i in range(100):
#             # 要改进一下
#             meta_path = random.choice(meta_pathes)
#             value = meta_path.match(pid)
#             if len(value) == 0:
#                 continue
#             value = tuple([parseRel(rel) for rel in value])
#             values.add(value)
#             value2attr[value] = meta_path.name
#             value2pid[value] = pid
#             all_values.add(value)
#         pid2values[pid] = values
#     return pid2values, value2attr, all_values, value2pid
#
#
# pid2values, value2att, all_values, value2pid = getPid2values(pid2person.keys())
#
#
# # print(sortDict(node2sup)[0:20])
# # print([getNodeName(node) for node, value in sortDict(node2related)][0:80])
# # print([getNodeName(node) for node, value in sortDict(node2sup)][0:80])
#
# def getSupport(n_id):
#     if n_id in node2sup:
#         return node2sup[n_id]
#     else:
#         print(n_id, '没算过支持度')
#         return 0
#
#
# def getRelevancy(n_id):
#     if n_id in node2sup:
#         return node2relevancy[n_id]
#     else:
#         # print(n_id, '没算过支持度')
#         return 0
#
#
# def parseRels(rels):
#     sentence = []
#     for s, t, r in rels:
#         sentence += [s, r, t]
#     return sentence
#
#
# def getValueRelevancy(value):
#     sentence = parseRels(value)
#     r = 0
#     for word in sentence:
#         r += getRelevancy(word)
#     return r / len(sentence)
#
#
# value2relevancy = {value: getValueRelevancy(value) for value in all_values}
#
# # for value, r in sortDict(value2relevancy)[:30]:
# #     print(value, r)
# # exit()
#
# # def randomWalk(node_id, G, depth = 3, sentence_num = 3):
# #     walked_rs = set()
# #     sentences = []
#
# #     for e in range(sentence_num):
# #         now_node = node_id
# #         sentence = [now_node]
# #         for d in range(depth):
# #             rels = getOutRels(now_node)
# #             if len(rels) == 0:
# #                 break
# #             neibor_props = [
# #                 getRelevancy(target)
# #                 for source, target, r_id in rels
# #             ]
#
# #             rel = weight_choice(rels, neibor_props)
# #             source, target, r_id = rel
# #             walked_rs.add(r_id)
# #             now_node = target
# #             sentence += [getRelLabel(r_id), getNodeName(target)]
# #         sentences.append(tuple(sentence))
#
# #     return sentences
#
# node_name2label = {}
# label2node_names = {}
# for node_name in node2relevancy:
#     if node_name == 'None':
#         continue
#     # print(node_name)
#     node_id = node_name2node_id[node_name]
#     label = getNodeLabel(node_id)
#     if label not in label2node_names:
#         label2node_names[label] = []
#     label2node_names[label].append(node_name)
#     node_name2label[node_name] = label
#
# label2ppl_nodes = {}
# ppl_nodes = []
# name2label = {}
# name2id = {}
#
# node2values = {}
# # print(all_values)
# # 多少能算显著特性
# for label, node_names in label2node_names.items():
#     # 为了加快
#     if label in ['PostType', 'AddrType', ]:
#         continue
#
#     popular_nodes = [node for node, value in sortDict({node_name: getRelevancy(node_name) for node_name in node_names})]
#     popular_nodes = [
#                         node
#                         for node in popular_nodes
#                         if node not in ['None', '0', '未详', '[未详]']
#                     ][:15]
#
#     filter_popular_nodes = []
#     for ppl_node in popular_nodes:
#         values = [sentence for sentence in all_values if ppl_node in parseRels(sentence)]
#         values = maxN(values, key=lambda item: value2relevancy[item])
#
#         involved_pids = set([value2pid[value] for value in values])
#         if len(involved_pids) > len(info_people) * 0.3:  # 剃掉那些不算不上群体的
#             filter_popular_nodes.append(ppl_node)
#             node2values[ppl_node] = values
#     ppl_nodes += filter_popular_nodes
#     label2ppl_nodes[label] = filter_popular_nodes
#
# print(label2ppl_nodes, ppl_nodes)
# # exit()
# # ppl_nodes = set(ppl_nodes)
# # for ppl_name in ppl_nodes:
# #     for p_id, values in pid2values:
# #         sentences = [sentence for sentence in all_values if ppl_name in parseRels(sentence)]
#
# ppl_node_set = set(ppl_nodes)
#
# # 计算节点
#
# # 改成了同一个人中出现的概率
#
# count_xy = {}
# count_x = {}
#
# # pmis = []
# for node1 in ppl_nodes:
#     count_xy[node1] = {node: 0 for node in ppl_nodes}
#     count_x[node1] = 0
#     for values in pid2values.values():
#         for value in values:
#             if value in node2values[node1]:
#                 count_x[node1] += 1
#                 break
#
#     for node2 in ppl_nodes:
#         # if node1 == node2:
#         #     print(1)
#         for values in pid2values.values():
#             has_node1 = has_node2 = False
#             for value in values:
#                 if value in node2values[node1]:
#                     has_node1 = True
#                     # if node1 == node2:
#                     #     print(value in node2values[node2])
#                 if value in node2values[node2]:
#                     has_node2 = True
#             if has_node1 and has_node2:
#                 count_xy[node1][node2] += 1
#
# # print(count_x)
# # print(count_xy)
# # showMatrix(count_xy)
# # exit()
#
#
# pmi_node = {}
# for node_x in ppl_nodes:
#     pmi_node[node_x] = {}
#     for node_y in ppl_nodes:
#         # print(node_x, node_y, count_x[node_x], count_x[node_y])
#         if count_x[node_x] == 0 or count_x[node_y] == 0:
#             pmi_node[node_x][node_y] = 0
#             continue
#         pxy = count_xy[node_x][node_y] / count_x[node_y]  # p(x|y)
#         px = count_x[node_x] / len(all_values)  # p(x)
#         pmi = pxy / px
#         if pmi == 0 or node_x == node_y:
#             pmi_node[node_x][node_y] = 0
#         else:
#             pmi_node[node_x][node_y] = math.log(pmi)
#         # pmis.append(pmi)
# # print(pmi_node)
#
# pmi_label = {}
# for label, nodes in label2ppl_nodes.items():
#     pmi_label[label] = {}
#     for temp_label, temp_nodes in label2ppl_nodes.items():
#         pmi = 0
#         for node in nodes:
#             for temp_node in temp_nodes:
#                 pxy = count_xy[node][temp_node] / len(all_values)  # P(x,y)
#                 pmi += pxy * pmi_node[node][temp_node]
#         if label == temp_label:
#             pmi_label[label][temp_label] = 0
#         else:
#             pmi_label[label][temp_label] = pmi
#         # print(label, temp_label, pmi)
#
# # print(pmi_label)
#
# # exit()
# # pmis = sorted(pmis, reverse=True)
#
# # node2sup = {node: 0 for node in ppl_nodes}
# # for sentence in all_sentencpes:
# #     for word in sentence:
# #         if word in node2sup:
# #             node2sup[word] += 1
# # # node2sup = {name2id: 0 for name, value in node2sup.items()}
#
#
# import numpy as np
# import matplotlib.pyplot as plt
# import pylab
# import matplotlib as mpl
#
# from matplotlib import rcParams
# from matplotlib.font_manager import FontProperties
#
# # linux去除中文乱码
# # ch_font =  FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',size=20)
# # rcParams['axes.unicode_minus']=False #解决负号'-'显示为方块的问题
# # mpl.rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
#
# # Windows去除中文乱码
# plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
# plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
#
#
# # 把label当做属性
#
# def showMatrix(a2a):
#     elm_len = len(a2a)
#     M = np.zeros((elm_len, elm_len))
#     for index_x, node_x in enumerate(a2a):
#         for index_y, node_y in enumerate(a2a):
#             M[index_x][index_y] = a2a[node_x][node_y]
#     print(M)
#     plt.matshow(M)
#     plt.yticks(list(range(elm_len)), a2a.keys())
#     plt.xticks(list(range(elm_len)), a2a.keys())
#     plt.show()
#
#
# # showMatrix(pmi_node)
# # showMatrix(pmi_label)
#
# # # 对节点降维
# # # pmis = [pmi for pmi in pmis if pmi != pmis[0]]
# # # print(pmis)
# # ppl_node_len = len(ppl_nodes)
# # ppl_dist = np.zeros((ppl_node_len, ppl_node_len))
# # for index_x, node_x in enumerate(ppl_nodes):
# #     for index_y, node_y in enumerate(ppl_nodes):
# #         pmi = pmi_node[node_x][node_y]
# #         ppl_dist[index_x][index_y] = -pmi #abs(pmi)
# #         # max_pmi-pmi
# #         # if pmi > 0 and node_x != node_y:
# #         #     print(node_x, node_y, pmi, dist[index_x][index_y])
#
# # # for key, item in pmi_xy.items():
# # #     print(key, sortDict(item)[: 10])
#
# # # x_values=
# # #x轴的数字是0到10这11个整数
# # # y_values= ppl_node
# # #y轴的数字是x轴数字的平方
# # # plt.plot(ppl_nodes, ppl_nodes)
#
# # # FontProperties = ch_font
# # # Display matrix
# # plt.matshow(ppl_dist)
# # plt.yticks(list(range(ppl_node_len)), ppl_nodes)
# # plt.xticks(list(range(ppl_node_len)), ppl_nodes)
# # plt.show()
#
# value2sentence = {}
# sentence2value = {}
# for value in all_values:
#     sentence = tuple(parseRels(value))
#     value2sentence[value] = sentence
#     sentence2value[sentence] = value
#
# all_sentences = value2sentence.values()
#
#
# # words = []
# # for sentence in all_sentences:
# #     words += list(sentence)
# # words = set(words)
# # # print(len(words), len(all_sentences))
#
# # print(node2relevancy)
# def countWord(s):
#     word2count = {w: 0 for w in s}
#     for w in s:
#         word2count[w] += 1
#     return word2count
#
#
# # 仿照tf-idf写的
# def calSim(v1, v2):
#     s1 = value2sentence[v1]
#     s2 = value2sentence[v2]
#
#     all_words = set([w for w in s1] + [w for w in s2])
#     if 'None' in all_words:
#         all_words.remove('None')
#     count1 = countWord(s1)
#     count2 = countWord(s2)
#
#     m1 = np.zeros(len(all_words))
#     m2 = np.zeros(len(all_words))
#
#     for index, w in enumerate(all_words):
#         r = getRelevancy(w)  # 现在没有算边的相关度
#         if r == 0:
#             r = 0.1
#         if w in count1:
#             m1[index] = count1[w] / r
#             # node2relevancy[w]
#         if w in count2:
#             m2[index] = count2[w] / r
#     # print(m1, m2)
#     return cos_dist(m1, m2)
#
#
# # # 计算句子的相似度数
# # from gensim import corpora, models, similarities
# # import gensim
#
# # dictionary= corpora.Dictionary(all_sentences)
# # corpus = [dictionary.doc2bow(sentence) for sentence in all_sentences]
# # tfidf_model = models.TfidfModel(corpus)
#
#
# from gensim.models import Word2Vec, Doc2Vec
# from gensim.models.doc2vec import TaggedDocument
#
# sent_model_path = "./model/sentence2vec.model"
# model = Doc2Vec.load(sent_model_path)
#
# # 人物降维
# value2vec = {}
# for node, values in node2values.items():
#     for value in values:
#         value2vec[value] = model.infer_vector(value2sentence[value])
#
# pid2vec = {p_id: np.zeros(100 * len(ppl_nodes)) for p_id in info_people_ids}
# for index, ppl_node in enumerate(ppl_nodes):
#     # print('index', index)
#     node_values = node2values[ppl_node]
#     node_vecs = [value2vec[value] for value in node_values]
#     mean = mean_vec(node_vecs)
#     # print(mean_vec)
#     for pid in info_people_ids:
#         max_dist_vec = mean
#
#         vecs = [value2vec[value] for value in pid2values[pid] if value in node_values]
#         if len(vecs) > 0:
#             max_dist_vec = max(vecs, key=lambda elm: cos_dist(elm, mean))
#         # 可以在这里加个维度的权重参数
#         pid2vec[pid][index * 100: index * 100 + 100] = max_dist_vec
#
# vecs = np.array([vec for pid, vec in pid2vec.items()])
# pid_vec2d = mds(2, data=vecs)
# colors = np.random.rand(len(info_people))
# plt.scatter(pid_vec2d[:, 0], pid_vec2d[:, 1], alpha=0.5, c=colors, )
# labels = [','.join(value2sentence[value]) for value in values]
# for index, pos in enumerate(pid_vec2d):
#     s = getNodeName(list(pid2vec.keys())[index])
#     x = pos[0]
#     y = pos[1]
#     # label = str(index) #p.get_pinyin(str(ppl_nodes[index]), tone_marks='marks')
#     plt.text(x, y, s, fontsize=5)
# plt.show()
#
# # for s1 in all_sentences:
# #     for s2 in all_sentences:
# #         print(s1, s2, calSim(s1, s2))
