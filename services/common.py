from gensim import models

from services.dao.cbdb_dao import CBDBDAO
from services.dao.graph_dao import GraphDAO
from services.entity.meta import build_meta_paths
from tools import yaml_utils

_labels = yaml_utils.read('./services/configs/labels.yaml')
NodeLabels = _labels['node']
EdgeLabels = _labels['edge']

CBDB_DAO = CBDBDAO('./dataset/CBDB_20190424.db')
GRAPH_DAO = GraphDAO('./dataset/graph.db')
GRAPH_DAO.start_connect()
NUM_ALL_PERSON = len(GRAPH_DAO.get_node_ids_by_label(NodeLabels['person']))
GRAPH_DAO.close_connect()
MetaPaths = build_meta_paths('./services/configs/meta_paths.yaml')
# Model = models.Doc2Vec.load('./services/models/sentence2vec.model')
Model = models.TfidfModel
Model_DIM = 100  # 模型的num维度
