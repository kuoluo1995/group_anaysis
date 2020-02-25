from services import common
from services.service import get_ranges_by_name, get_topics_by_person_ids, get_doc2vec
from utils.sort_utils import sort_dict2list

if __name__ == '__main__':
    NodeLabels = common.NodeLabels
    ranges = get_ranges_by_name('王安石')
    person_ids = ranges[NodeLabels['person']].keys()
    person_id2relation = {_id: len(common.DAO.get_in_edges(_id) + common.DAO.get_out_edges(_id)) for _id in person_ids}
    person_id2relation = sort_dict2list(person_id2relation)[:30]
    person_ids = [_id[0] for _id in person_id2relation]
    temp = get_topics_by_person_ids(person_ids)
    get_doc2vec(temp['topic2sentences'])
    # 将算法的结果保存成json串，用于提供给前端快速测试
    # input_file = 'input.json'  # 输入的json
    # with open(input_file, 'w') as file_obj:
    #     json.dump(person_ids, file_obj)
    # output_file = 'topic.json'  # 输出的json
    # with open(output_file, 'w') as file_obj:
    #     json.dump(temp, file_obj)
