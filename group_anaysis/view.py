import json
from django.http import HttpResponse
from django.shortcuts import render, render_to_response

from services.service import get_ranges_by_name, get_person_by_ranges, get_topics_by_person_ids


def test_html(request):
    return render_to_response('test_post.html')


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
    dynastie_id = min_year = max_year = gender_id = statu_id = None
    if 'dynastie_id' in request.POST and request.POST['dynastie_id']:
        dynastie_id = int(request.POST['dynastie_id'])
    if 'min_year' in request.POST and request.POST['min_year']:
        min_year = int(request.POST['min_year'])
    if 'max_year' in request.POST and request.POST['max_year']:
        max_year = int(request.POST['max_year'])
    if 'gender_id' in request.POST and request.POST['gender_id']:
        gender_id = int(request.POST['gender_id'])
    if 'statu_id' in request.POST and request.POST['statu_id']:
        statu_id = int(request.POST['statu_id'])
    if dynastie_id is not None and (
            min_year is not None or max_year is not None or gender_id is not None or statu_id is not None):
        result = get_person_by_ranges(dynastie_id, min_year, max_year, gender_id, statu_id)
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
    dynastie_id = min_year = max_year = gender_id = statu_id = None
    if 'dynastie_id' in request.POST and request.POST['dynastie_id']:
        dynastie_id = int(request.POST['dynastie_id'])
    if 'min_year' in request.POST and request.POST['min_year']:
        min_year = int(request.POST['min_year'])
    if 'max_year' in request.POST and request.POST['max_year']:
        max_year = int(request.POST['max_year'])
    if 'gender_id' in request.POST and request.POST['gender_id']:
        gender_id = int(request.POST['gender_id'])
    if 'statu_id' in request.POST and request.POST['statu_id']:
        statu_id = int(request.POST['statu_id'])
    if dynastie_id is not None and (
            min_year is not None or max_year is not None or gender_id is not None or statu_id is not None):
        result = get_person_by_ranges(dynastie_id, min_year, max_year, gender_id, statu_id)
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
