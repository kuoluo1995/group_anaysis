import random
from services.dao import sqlite_graph
from utils import yaml_utils

Labels = yaml_utils.read('./services/configs/labels.yaml')


class MetaNode:
    def __init__(self, label):
        self.label = label
        self.next_nodes = list()

    def match(self, start_node):
        all_edges = []
        node_label = sqlite_graph.get_node_label_by_id(start_node)
        if node_label != self.label:
            raise Exception(start_node, node_label, sqlite_graph.get_node_label_by_id(start_node), '不符合', self.label)
        for _label, _node in self.next_nodes:
            # 可以加个一定几率放弃游走
            _edges = sqlite_graph.get_out_edges(start_node)
            _edges = [(target, r_id) for source, target, r_id in _edges if
                      sqlite_graph.get_edge_label_by_id(r_id) == _label and sqlite_graph.get_node_label_by_id(
                          target) == _node.label]
            if len(_edges) == 0:
                continue
            target, r_id = random.choice(_edges)  # todo 为啥要随机游走？全部遍历不可以吗？
            all_edges.append((start_node, target, r_id))
            all_edges += _node.match(target)
        return all_edges

    def __str__(self):
        return str([(self.label, edge_label, _node.label) for edge_label, _node in self.next_nodes]) + str(
            [_node for r_label, _node in self.next_nodes])


class MetaPath:
    def __init__(self, name):
        self.start = MetaNode(Labels.person)
        self.name = name

    def match(self, start_node):
        return self.start.match(start_node)


# todo 可以全自动的
class MetaPathRule:
    def get_address_node(self):
        node = MetaNode(Labels.address)  # todo checked 循环？
        node.next_nodes = [(Labels.address_belong, MetaNode(Labels.address))]
        return node

    def get_office_node(self):
        office_type = MetaNode(Labels.office_type)
        office_type.next_nodes = [(Labels.office_belong, MetaNode(Labels.office_type))]
        office = MetaNode(Labels.office)
        office.next_nodes = [(Labels.office_belong, office_type)]  # todo checked
        return office

    def add_gender_path(self):
        path = MetaPath('性别')
        path.start.next_nodes = [(Labels.gender_is, MetaNode(Labels.gender))]

    def add_ethnicity_path(self):
        path = MetaPath('民族')
        path.start.next_nodes = [(Labels.enthnicity_is, MetaNode(Labels.ethnicity))]

    def add_post_path(self):
        post = MetaNode(Labels.post)
        post.next_nodes = [(Labels.fist_year, MetaNode(Labels.year)),
                           (Labels.last_year, MetaNode(Labels.year)),
                           (Labels.office_is, self.get_office_node()),
                           (Labels.post_is, MetaNode(Labels.post_type)),
                           (Labels.where, self.get_address_node())]
        path = MetaPath('官职')
        path.start.next_nodes = [(Labels.do, post)]

    def add_write_path(self):
        path = MetaPath('写作')
        path.start.next_nodes = [(Labels.text_is, MetaNode(Labels.text))]

    def add_associate_path(self):
        associate_event = MetaNode(Labels.associate_event)
        associate_event.next_nodes = [(Labels.associate_belong, MetaNode(Labels.association)),
                                      (Labels.associate_is, MetaNode(Labels.person)),
                                      (Labels.fist_year, MetaNode(Labels.year)),
                                      (Labels.occasion_is, MetaNode(Labels.occasion)),
                                      (Labels.topic_is, MetaNode(Labels.scholar)),
                                      (Labels.where, self.get_address_node())]
        path = MetaPath('关系')
        path.start.next_nodes = [(Labels.do, associate_event)]

    def add_house_hold_path(self):
        path = MetaPath('定位')
        path.start.next_nodes = [(Labels.house_hold_is, MetaNode(Labels.house_hold))]

    def add_status_path(self):
        path = MetaPath('社会区分')
        path.start.next_nodes = [(Labels.status_is, MetaNode(Labels.status))]

    def add_address_event_path(self):
        address_type = MetaNode(Labels.address_type)  # 这里是不对的 todo
        address_type.next_nodes = [(Labels.where, self.get_address_node())]
        path = MetaPath('地点事件')
        path.start.next_nodes = [(Labels.address_associate_is, address_type)]

    def add_entry_event_path(self):
        entry_type = MetaNode(Labels.entry_type) # todo checked循环？
        entry_type.next_nodes = [(Labels.entry_belong, MetaNode(Labels.entry_type))]
        entry = MetaNode(Labels.entry)
        entry.next_nodes = [(Labels.entry_is, entry_type)]
        entry_event = MetaNode(Labels.entry_event)
        entry_event.next_nodes = [(Labels.entry_is, entry),
                                  (Labels.fist_year, MetaNode(Labels.year)),
                                  (Labels.note_is, MetaNode(Labels.note))]

        path = MetaPath('入仕')
        path.start.next_nodes = [(Labels.do, entry_event)]
