import json
from django.http import HttpResponse

from services.service import get_ranges_by_name


def search_ranges_by_name(request):
    request.encoding = 'utf-8'
    result = {'is_success': False}
    if 'name' in request.GET and request.GET['name']:
        result = get_ranges_by_name(request.GET['name'])
        result.update({'is_success': True})
    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type="application/json")


def search_person_by_ranges(request):
    request.encoding = 'utf-8'
    result = {'is_success': False}
    if 'name' in request.GET and request.GET['name']:
        result = get_ranges_by_name(request.GET['name'])
        result.update({'is_success': True})
    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type="application/json")

# def search_person_by_ranges(request):
#     request.encoding = 'utf-8'
#     result = {'is_success': False}
#     if 'name' in request.GET and request.GET['name']:
#         result = get_ranges_by_name(request.GET['name'])
#         result.update({'is_success': True})
#     json_result = json.dumps(result)
#     return HttpResponse(json_result, content_type="application/json")
