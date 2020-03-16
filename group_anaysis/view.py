import json
from django.http import HttpResponse
from django.shortcuts import render

from services import common
from services.service import get_ranges_by_name, get_topics_by_person_ids, get_person_by_ranges, get_init_ranges, \
    get_address_by_person_ids, get_community_by_num_node_links, get_all_similar_person


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
        name = request.POST['name']
        try:
            labels = [NodeLabels['person'], NodeLabels['dynasty'], NodeLabels['year'], NodeLabels['gender'],
                      NodeLabels['status']]
            result.update(get_ranges_by_name(labels, name))
            result['is_success'] = True
        except Exception as e:
            result['bug'] = '发给后端调试问题。输入为 name:{}'.format(name)
    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type="application/json")


def search_person_by_ranges(request):
    NodeLabels = common.NodeLabels
    request.encoding = 'utf-8'
    result = {'is_success': False}
    dynasty_ids = min_year = max_year = is_female = statu_ids = None
    if 'dynasty_ids[]' in request.POST and request.POST['dynasty_ids[]']:
        dynasty_ids = request.POST.getlist('dynasty_ids[]')
    if 'min_year' in request.POST and request.POST['min_year']:
        min_year = request.POST['min_year']
    if 'max_year' in request.POST and request.POST['max_year']:
        max_year = request.POST['max_year']
    if 'genders[]' in request.POST and request.POST['genders[]'] and len(request.POST['genders[]']) == 1:
        is_female = (request.POST.getlist('genders[]')[0] == '女')
    if 'statu_ids[]' in request.POST and request.POST['statu_ids[]']:
        statu_ids = request.POST.getlist('statu_ids[]')
    try:
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
    if 'person_ids[]' in request.POST and request.POST['person_ids[]']:
        person_ids = request.POST.getlist('person_ids[]')
        try:
            address = get_address_by_person_ids(person_ids)
            result[NodeLabels['address']] = address
            result['is_success'] = True
        except Exception as e:
            result['bug'] = '发给后端调试问题。输入为 person_ids:{}'.format(person_ids)
    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type="application/json")


def search_topics_by_person_ids(request):
    request.encoding = 'utf-8'
    result = {'is_success': False}
    if 'person_ids[]' in request.POST and request.POST['person_ids[]']:
        person_ids = request.POST.getlist('person_ids[]')
        try:
            person_ids = [int(_id) for _id in person_ids]
            all_topic_ids, topic_id2sentence_id2position1d, topic_pmi, person_id2position2d, node_dict, edge_dict, topic_id2lrs, similar_person_ids = get_topics_by_person_ids(
                person_ids, max_topic=15)
            result['all_topic_ids'] = [[int(_id) for _id in _ids] for _ids in all_topic_ids]
            topic_id2sentence_id2position1d_json = {}
            for _topic_id, _item in topic_id2sentence_id2position1d.items():
                _topic_id = [str(_id) for _id in _topic_id]
                _topic_id = ' '.join(_topic_id)
                topic_id2sentence_id2position1d_json[_topic_id] = {}
                for _sentence_id, _value in _item.items():
                    _sentence = [str(_id) for _id in _sentence_id]
                    _sentence = ' '.join(_sentence)
                    topic_id2sentence_id2position1d_json[_topic_id][_sentence] = _value[0]
            result['topic_id2sentence_id2position1d'] = topic_id2sentence_id2position1d_json
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
            result['similar_person_ids'] = similar_person_ids
            result['is_success'] = True
        except Exception as e:
            result['bug'] = '发给后端调试问题。输入为 person_ids:{}'.format(person_ids)
    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type="application/json")


def search_community_by_links(request):
    request.encoding = 'utf-8'
    result = {'is_success': False}
    if 'num' in request.POST and request.POST['num'] and 'links' in request.POST and request.POST['links']:
        num_node = request.POST['num']
        links = request.POST['links'].split(',')
        try:
            partition = get_community_by_num_node_links(num_node, links)
            result['data'] = partition
            result['info'] = '社团发现'
            result['is_success'] = True
        except Exception as e:
            result['bug'] = '发给后端调试问题。输入为 num:{},links:{}'.format(num_node, links)
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
