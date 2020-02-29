import json
from django.http import HttpResponse
from django.shortcuts import render

from services.service import get_ranges_by_name, delete_person_by_ranges, get_topics_by_person_ids, get_init_ranges, \
    get_person_by_dynastie


def test_init_ranges(request):
    request.encoding = 'utf-8'
    result = get_init_ranges()
    json_result = json.dumps(result)
    return render(request, 'test_post.html', {'result': json_result})


def test_search_ranges_by_name(request):
    request.encoding = 'utf-8'
    result = {'is_success': False}
    if 'name' in request.POST and request.POST['name']:
        result = get_ranges_by_name(request.POST['name'])
        result['is_success'] = True
    json_result = json.dumps(result)
    return render(request, 'test_post.html', {'result': json_result})


def test_search_person_by_dynastie(request):
    request.encoding = 'utf-8'
    result = {'is_success': False}
    if 'dynastie' in request.POST and request.POST['dynastie']:
        result = get_person_by_dynastie(request.POST['dynastie'])
        result['is_success'] = True
    json_result = json.dumps(result)
    return render(request, 'test_post.html', {'result': json_result})


def test_filter_person_by_ranges(request):
    request.encoding = 'utf-8'
    result = {'is_success': False}
    if 'person_ids' in request.POST and request.POST['person_ids']:
        min_year = max_year = genders = status = None
        all_person = request.POST['person_ids'].split(';')
        if len(all_person) > 50:
            all_person = all_person[:50]
        if 'min_year' in request.POST and request.POST['min_year']:
            min_year = int(request.POST['min_year'])
        if 'max_year' in request.POST and request.POST['max_year']:
            max_year = int(request.POST['max_year'])
        if 'genders' in request.POST and request.POST['genders']:
            genders = request.POST['genders'].split(';')
        if 'status' in request.POST and request.POST['status']:
            status = request.POST['status'].split(';')
        if all_person is not None and len(all_person) > 0:
            result = delete_person_by_ranges(all_person, min_year, max_year, genders, status)
            result['is_success'] = True
        json_result = json.dumps(result)
        return render(request, 'test_post.html', {'result': json_result})


def test_search_topics_by_person_ids(request):
    request.encoding = 'utf-8'
    result = {'is_success': False}
    if 'person_ids' in request.POST and request.POST['person_ids']:
        person_ids = request.POST['person_ids'].split(';')
        person_ids = [int(_id) for _id in person_ids]
        result = get_topics_by_person_ids(person_ids)
        result['is_success'] = True
    json_result = json.dumps(result)
    return render(request, 'test_post.html', {'result': json_result})


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


def search_person_by_dynastie(request):
    request.encoding = 'utf-8'
    result = {'is_success': False}
    if 'dynastie' in request.POST and request.POST['dynastie']:
        try:
            result = get_person_by_dynastie(request.POST['dynastie'])
            result['is_success'] = True
        except Exception as e:
            result['bug'] = '发给后端调试问题。输入为 dynastie:{}'.format(request.POST['dynastie'])
    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type="application/json")


def filter_person_by_ranges(request):
    request.encoding = 'utf-8'
    result = {'is_success': False}
    all_person = min_year = max_year = genders = status = None
    if 'person_ids' in request.POST and request.POST['person_ids']:
        all_person = request.POST['person_ids']
    if 'min_year' in request.POST and request.POST['min_year']:
        min_year = int(request.POST['min_year'])
    if 'max_year' in request.POST and request.POST['max_year']:
        max_year = int(request.POST['max_year'])
    if 'genders' in request.POST and request.POST['genders'] and len(request.POST['genders']) > 0:
        genders = request.POST['genders']
    if 'status' in request.POST and request.POST['status'] and len(request.POST['status']) > 0:
        status = request.POST['status']
    if all_person is not None and len(all_person) > 0:
        try:
            result = delete_person_by_ranges(all_person, min_year, max_year, genders, status)
            result['is_success'] = True
        except Exception as e:
            result['bug'] = '发给后端调试问题。输入为 person_ids:{} min_year:{} max_year:{} genders:{} status:{}' \
                .format(all_person, min_year, max_year, genders, status)
    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type="application/json")


def search_topics_by_person_ids(request):
    request.encoding = 'utf-8'
    result = {'is_success': False}
    # if 'person_ids' in request.POST and request.POST['person_ids'] and len(request.POST['person_ids']) > 0:
    person_ids = request.POST.getlist('person_ids[]')
    if person_ids is not None and len(person_ids) > 0:
        try:
            result = get_topics_by_person_ids(person_ids)
            result['is_success'] = True
        except Exception as e:
            result['bug'] = '发给后端调试问题。输入为 person_ids:{}'.format(person_ids)
    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type="application/json")
