import json
from django.http import HttpResponse
from django.shortcuts import render

from services.service import get_ranges_by_name, get_person_by_ranges, get_topics_by_person_ids, get_init_ranges


def test_init_ranges(request):
    request.encoding = 'utf-8'
    result = get_init_ranges()
    result['is_success'] = True
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


def test_search_person_by_ranges(request):
    request.encoding = 'utf-8'
    result = {'is_success': False}
    dynastie = min_year = max_year = genders = status = None
    if 'dynastie' in request.POST and request.POST['dynastie']:
        dynastie = request.POST['dynastie']
    if 'min_year' in request.POST and request.POST['min_year']:
        min_year = int(request.POST['min_year'])
    if 'max_year' in request.POST and request.POST['max_year']:
        max_year = int(request.POST['max_year'])
    if 'genders' in request.POST and request.POST['genders']:
        genders = request.POST['genders'].split(';')
    if 'status' in request.POST and request.POST['status']:
        status = request.POST['status'].split(';')
    if dynastie is not None:
        result = get_person_by_ranges(dynastie, min_year, max_year, genders, status)
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
    result = get_init_ranges()
    result['is_success'] = True
    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type="application/json")


def search_ranges_by_name(request):
    request.encoding = 'utf-8'
    result = {'is_success': False}
    if 'name' in request.POST and request.POST['name']:
        result = get_ranges_by_name(request.POST['name'])
        result['is_success'] = True
    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type="application/json")


def search_person_by_ranges(request):
    request.encoding = 'utf-8'
    result = {'is_success': False}
    dynastie = min_year = max_year = genders = status = None
    if 'dynastie' in request.POST and request.POST['dynastie']:
        dynastie = request.POST['dynastie']
    if 'min_year' in request.POST and request.POST['min_year']:
        min_year = int(request.POST['min_year'])
    if 'max_year' in request.POST and request.POST['max_year']:
        max_year = int(request.POST['max_year'])
    if 'genders' in request.POST and request.POST['genders'] and len(request.POST['genders']) > 0:
        genders = request.POST['genders']
    if 'status' in request.POST and request.POST['status'] and len(request.POST['status']) > 0:
        status = request.POST['status']
    if dynastie is not None:
        result = get_person_by_ranges(dynastie, min_year, max_year, genders, status)
        result['is_success'] = True
    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type="application/json")


def search_topics_by_person_ids(request):
    request.encoding = 'utf-8'
    result = {'is_success': False}
    if 'person_ids' in request.POST and request.POST['person_ids'] and len(request.POST['person_ids']) > 0:
        result = get_topics_by_person_ids(request.POST['person_ids'])
        result['is_success'] = True
    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type="application/json")
