from gensim import models

from services.dao.cbdb_dao import CBDBDAO
from services.dao.graph_dao import GraphDAO
from services.dao.neo4j_dao import Neo4jDAO
from services.entity.meta import build_meta_paths
from tools import yaml_utils
from tools.shell_utils import Shell

_labels = yaml_utils.read('./services/configs/labels.yaml')
NodeLabels = _labels['node']
EdgeLabels = _labels['edge']

CBDB_DAO = CBDBDAO('./dataset/CBDB_20190424.db')
GRAPH_DAO = GraphDAO('./dataset/graph.db')
GRAPH_DAO.start_connect()
NUM_ALL_PERSON = len(GRAPH_DAO.get_node_ids_by_label(NodeLabels['person']))
GRAPH_DAO.close_connect()
# 如果没有图数据库需求的可以注释掉下面的内容
neo4j = Shell('neo4j.bat console', 'Started')
neo4j.run_background()
NEO4J_DAO = Neo4jDAO('bolt://localhost:7687', 'neo4j', '123456')

MetaPaths = build_meta_paths('./services/configs/meta_paths.yaml')
# Model = models.Doc2Vec.load('./services/models/sentence2vec.model')
Model = models.TfidfModel
Model_DIM = 5  # 模型的num维度
