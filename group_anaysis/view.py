import json
from django.http import HttpResponse
from django.shortcuts import render

from services.service import get_ranges_by_name, get_topics_by_person_ids, get_person_by_ranges, get_init_ranges, \
    get_address_by_person_ids


def init_ranges(request):
    request.encoding = 'utf-8'
    result = {'is_success': False}
    try:
        result = get_init_ranges()
        result['is_success'] = True
    except Exception as e:
        result['bug'] = '发给后端调试问题。输入为 空'
    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type="application/json")


def search_ranges_by_name(request):
    request.encoding = 'utf-8'
    result = {'is_success': False}
    if 'name' in request.POST and request.POST['name']:
        try:
            result = get_ranges_by_name(request.POST['name'])
            result['is_success'] = True
        except Exception as e:
            result['bug'] = '发给后端调试问题。输入为 name:{}'.format(request.POST['name'])
    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type="application/json")


def search_person_by_ranges(request):
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
        result = get_person_by_ranges(dynasty_ids, min_year, max_year, is_female, statu_ids)
        result['is_success'] = True
    except Exception as e:
        result['bug'] = '发给后端调试问题。输入为 dynasty_ids:{} min_year:{} max_year:{} is_female:{} statu_ids:{}' \
            .format(dynasty_ids, min_year, max_year, is_female, statu_ids)
    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type="application/json")


def search_address_by_person_ids(request):
    request.encoding = 'utf-8'
    result = {'is_success': False}
    if 'person_ids[]' in request.POST and request.POST['person_ids[]'] and len(request.POST['person_ids[]']) > 0:
        try:
            person_ids = request.POST.getlist('person_ids[]')
            result = get_address_by_person_ids(person_ids)
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
            result = get_topics_by_person_ids(person_ids)
            result['is_success'] = True
        except Exception as e:
            result['bug'] = '发给后端调试问题。输入为 person_ids:{}'.format(request.POST['person_ids[]'])
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
