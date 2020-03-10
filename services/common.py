from gensim.models import Doc2Vec

from services.dao.cbdb_dao import CBDBDAO
from services.dao.graph_dao import GraphDAO
from services.entity.meta import build_meta_paths
from tools import yaml_utils

_labels = yaml_utils.read('./services/configs/labels.yaml')
NodeLabels = _labels['node']
EdgeLabels = _labels['edge']
CBDB_DAO = CBDBDAO('./dataset/CBDB_20190424.db')
GRAPH_DAO = GraphDAO('./dataset/graph.db')
MetaPaths = build_meta_paths('./services/configs/meta_paths.yaml')
Model = Doc2Vec.load('./services/models/sentence2vec.model')
Model_DIM = 100  # 模型的num维度
