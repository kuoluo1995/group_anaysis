import traceback

from channels.generic.websocket import WebsocketConsumer
import json

from services.service import get_topics_by_person_ids


class SocketSearchTopicsByPersonIds(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        request = json.loads(text_data)
        result = {'is_success': False}
        if 'person_ids[]' in request and request['person_ids[]'] and 'populate_ratio' in request and request['populate_ratio'] and 'max_topic' in request and request['max_topic'] and 'min_sentence' in request and request['min_sentence']:
            person_ids = request['person_ids[]']
            person_ids = [int(_id) for _id in person_ids]
            populate_ratio = float(request['populate_ratio'])
            max_topic = int(request['max_topic'])
            min_sentence = int(request['min_sentence'])
            try:
                print('查询的人:{}'.format(person_ids))
                all_topic_ids, topic_id2sentence_ids2position1d, topic_pmi, person_id2position2d, node_dict, edge_dict, topic_id2lrs, all_sentence_dict, topic_id2sentence_ids2vector, person_id2sentence_ids = get_topics_by_person_ids(
                    person_ids, populate_ratio=populate_ratio, max_topic=max_topic, min_sentence=min_sentence)
                result['all_topic_ids'] = [[int(_id) for _id in _ids] for _ids in all_topic_ids]
                topic_id2sentence_ids2position1d_json = {}
                for _topic_id, _item in topic_id2sentence_ids2position1d.items():
                    _topic_id = [str(_id) for _id in _topic_id]
                    _topic_id = ' '.join(_topic_id)
                    topic_id2sentence_ids2position1d_json[_topic_id] = {}
                    for _sentence_id, _value in _item.items():
                        _sentence = [str(_id) for _id in _sentence_id]
                        _sentence = ' '.join(_sentence)
                        topic_id2sentence_ids2position1d_json[_topic_id][_sentence] = [v for v in _value]
                result['topic_id2sentence_id2position1d'] = topic_id2sentence_ids2position1d_json
                topic_pmi_json = {}
                for _xs, _item in topic_pmi.items():
                    _xs = [str(_id) for _id in _xs]
                    _xs = ' '.join(_xs)
                    topic_pmi_json[_xs] = {}
                    for _ys, _pmi in _item.items():
                        _ys = [str(_id) for _id in _ys]
                        _ys = ' '.join(_ys)
                        topic_pmi_json[_xs][_ys] = _pmi
                result['topic_pmi'] = topic_pmi_json
                result['person_id2position2d'] = person_id2position2d
                result['node_dict'] = node_dict
                result['edge_dict'] = edge_dict
                topic_id2lrs_json = {}
                for _topic_id, _lrs in topic_id2lrs.items():
                    _topic_id = [str(_id) for _id in _topic_id]
                    _topic_id = ' '.join(_topic_id)
                    topic_id2lrs_json[_topic_id] = _lrs
                result['topic_id2lrs'] = topic_id2lrs_json
                all_sentence_dict_json = {}
                for _sentence_id, _name in all_sentence_dict.items():
                    _sentence_id = [str(_id) for _id in _sentence_id]
                    _sentence_id = ' '.join(_sentence_id)
                    all_sentence_dict_json[_sentence_id] = _name
                result['all_sentence_dict'] = all_sentence_dict_json
                topic_id2sentence_ids2vector_json = {}
                for _topic_id, _item in topic_id2sentence_ids2vector.items():
                    _topic_id = [str(_id) for _id in _topic_id]
                    _topic_id = ' '.join(_topic_id)
                    topic_id2sentence_ids2vector_json[_topic_id] = {}
                    for _sentence_id, _value in _item.items():
                        _sentence = [str(_id) for _id in _sentence_id]
                        _sentence = ' '.join(_sentence)
                        topic_id2sentence_ids2vector_json[_topic_id][_sentence] = {}
                        for _s, _f in _value.items():
                            _s = [str(_id) for _id in _s]
                            _s = ' '.join(_s)
                            topic_id2sentence_ids2vector_json[_topic_id][_sentence][_s] = float(_f)
                result['topic_id2sentence_ids2vector'] = topic_id2sentence_ids2vector_json
                person_id2sentence_ids = {_person_id: list(_sentence_id) for _person_id, _sentence_id in
                                          person_id2sentence_ids.items()}
                result['person_id2sentence_ids'] = person_id2sentence_ids
                result['is_success'] = True
            except Exception as e:
                traceback.print_exc()
                result['bug'] = '发给后端调试问题。输入为 {}'.format(text_data)
        json_result = json.dumps(result)
        self.send(text_data=json_result)
