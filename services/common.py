from gensim.models import Doc2Vec

from services.dao import SqliteGraphDAO
from services.entity.meta import build_meta_paths
from utils import yaml_utils

_labels = yaml_utils.read('./services/configs/labels.yaml')
NodeLabels = _labels['node']
EdgeLabels = _labels['edge']
DAO = SqliteGraphDAO('./dataset/graph.db')
MetaPaths = build_meta_paths('./services/configs/meta_paths.yaml')
Model = Doc2Vec.load('./services/models/sentence2vec.model')
