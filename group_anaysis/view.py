import json

import gc
from django.http import HttpResponse
from django.shortcuts import render

from services import common
from services.service import get_ranges_by_name, get_topics_by_person_ids, get_person_by_ranges, get_init_ranges, \
    get_address_by_person_ids, get_community_by_num_node_links


def init_ranges(request):
    NodeLabels = common.NodeLabels
    request.encoding = 'utf-8'
    result = {'is_success': False}
    try:
        dynasties, status = get_init_ranges()
        result[NodeLabels['dynasty']] = dynasties
        result[NodeLabels['status']] = status
        result['is_success'] = True
    except Exception as e:
        result['bug'] = '发给后端调试问题。输入为 空'
    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type="application/json")


def search_ranges_by_name(request):
    NodeLabels = common.NodeLabels
    request.encoding = 'utf-8'
    result = {'is_success': False}
    if 'name' in request.POST and request.POST['name']:
        try:
            labels = [NodeLabels['person'], NodeLabels['dynasty'], NodeLabels['year'], NodeLabels['gender'],
                      NodeLabels['status']]
            result.update(get_ranges_by_name(labels, request.POST['name']))
            result['is_success'] = True
        except Exception as e:
            result['bug'] = '发给后端调试问题。输入为 name:{}'.format(request.POST['name'])
    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type="application/json")


def search_person_by_ranges(request):
    NodeLabels = common.NodeLabels
    request.encoding = 'utf-8'
    result = {'is_success': False}
    dynasty_ids = min_year = max_year = is_female = statu_ids = None
    try:
        if 'dynasty_ids[]' in request.POST and request.POST['dynasty_ids[]'] and len(request.POST['dynasty_ids[]']) > 0:
            dynasty_ids = request.POST.getlist('dynasty_ids[]')
        if 'min_year' in request.POST and request.POST['min_year']:
            min_year = request.POST['min_year']
        if 'max_year' in request.POST and request.POST['max_year']:
            max_year = request.POST['max_year']
        if 'genders[]' in request.POST and request.POST['genders[]'] and len(request.POST['genders[]']) == 1:
            is_female = (request.POST.getlist('genders[]')[0] == '女')
        if 'statu_ids[]' in request.POST and request.POST['statu_ids[]'] and len(request.POST['statu_ids[]']) > 0:
            statu_ids = request.POST.getlist('statu_ids[]')
        person = get_person_by_ranges(dynasty_ids, min_year, max_year, is_female, statu_ids)
        result[NodeLabels['person']] = person
        result['is_success'] = True
    except Exception as e:
        result['bug'] = '发给后端调试问题。输入为 dynasty_ids:{} min_year:{} max_year:{} is_female:{} statu_ids:{}' \
            .format(dynasty_ids, min_year, max_year, is_female, statu_ids)
    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type="application/json")


def search_address_by_person_ids(request):
    NodeLabels = common.NodeLabels
    request.encoding = 'utf-8'
    result = {'is_success': False}
    if 'person_ids[]' in request.POST and request.POST['person_ids[]'] and len(request.POST['person_ids[]']) > 0:
        try:
            person_ids = request.POST.getlist('person_ids[]')
            address = get_address_by_person_ids(person_ids)
            result[NodeLabels['address']] = address
            result['is_success'] = True
        except Exception as e:
            result['bug'] = '发给后端调试问题。输入为 person_ids:{}'.format(request.POST['person_ids[]'])
    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type="application/json")


def search_topics_by_person_ids(request):
    request.encoding = 'utf-8'
    result = {'is_success': False}
    if 'person_ids[]' in request.POST and request.POST['person_ids[]'] and len(request.POST['person_ids[]']) > 0:
        try:
            person_ids = request.POST.getlist('person_ids[]')
            person_ids = [int(_id) for _id in person_ids]
            all_topic_ids, label2topic_ids, topic_id2sentence_id2position1d, topic_pmi, person_id2position2d, node_dict, edge_dict = get_topics_by_person_ids(
                person_ids)
            # todo 未来可以考虑去掉？可以通过topic2sentence_positions来获取？
            result['all_topic_ids'] = [int(_id) for _id in all_topic_ids]
            label2topic_ids_json = {}
            for _label, _ids in label2topic_ids.items():
                label2topic_ids_json[_label] = [int(_id) for _id in _ids]

            result['label2topic_ids'] = label2topic_ids_json
            topic_id2sentence_id2position1d_json = {}
            for _topic_id, _item in topic_id2sentence_id2position1d.items():
                topic_id2sentence_id2position1d_json[int(_topic_id)] = {}
                for _sentence_id, _value in _item.items():
                    _sentence = [str(_id) for _id in _sentence_id]
                    _sentence = ' '.join(_sentence)
                    topic_id2sentence_id2position1d_json[int(_topic_id)][_sentence] = _value

            result['topic_id2sentence_id2position1d'] = topic_id2sentence_id2position1d_json
            node_pmi_json = {}
            for _x, _item in topic_pmi.items():
                node_pmi_json[int(_x)] = {}
                for _y, _pmi in _item.items():
                    node_pmi_json[int(_x)][int(_y)] = _pmi

            result['topic_pmi'] = node_pmi_json
            result['person_id2position2d'] = person_id2position2d
            result['node_dict'] = node_dict
            result['edge_dict'] = edge_dict
            result['is_success'] = True
        except Exception as e:
            result['bug'] = '发给后端调试问题。输入为 person_ids:{}'.format(request.POST['person_ids[]'])
    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type="application/json")


def search_community_by_links(request):
    request.encoding = 'utf-8'
    result = {'is_success': False}
    if 'num' in request.POST and request.POST['num'] and 'links' in request.POST and request.POST['links']:
        try:
            num_node = request.POST['num']
            links = request.POST['links'].split(',')
            partition = get_community_by_num_node_links(num_node, links)
            result['data'] = partition
            result['info'] = '社团发现'
            result['is_success'] = True
        except Exception as e:
            result['bug'] = '发给后端调试问题。输入为 num:{},links:{}'.format(request.POST['num'], request.POST['links'])
    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type="application/json")


def test_init_ranges(request):
    response = init_ranges(request)
    content = str(response.content, 'utf-8')
    return render(request, 'test_post.html', {'response': content})


def test_search_ranges_by_name(request):
    response = search_ranges_by_name(request)
    content = str(response.content, 'utf-8')
    return render(request, 'test_post.html', {'response': content})


def test_search_person_by_ranges(request):
    response = search_person_by_ranges(request)
    content = str(response.content, 'utf-8')
    return render(request, 'test_post.html', {'response': content})


def test_search_address_by_person_ids(request):
    response = search_address_by_person_ids(request)
    content = str(response.content, 'utf-8')
    return render(request, 'test_post.html', {'response': content})


def test_search_topics_by_person_ids(request):
    response = search_topics_by_person_ids(request)
    content = str(response.content, 'utf-8')
    return render(request, 'test_post.html', {'response': content})
