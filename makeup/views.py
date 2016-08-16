import json
import requests
import urllib
from copy import deepcopy
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
from django.views.generic.base import TemplateView
from makeup.models import Product

client = settings.ES_CLIENT

def autocomplete_view(request):
    query = request.GET.get('term', '')

    data = {
               "size": 5,
               "query": {
                  "match": {
                     "_all": {
                        "query": query,
                        "operator": "and"
                     }
                  }
               }
            }
    post_request = requests.post('http://localhost:9200/django/_search?pretty=true', json.dumps(data))
    result = []
    resp = json.loads(post_request.content)
    if resp['hits']['total'] == 0:
        data = {
                   "size": 5,
                   "query": {
                      "match": {
                         "_all": {
                            "query": query,
                            "operator": "or",
                            "fuzziness": 1
                         }
                      }
                   }
                }
        post_request = requests.post('http://localhost:9200/django/_search?pretty=true', json.dumps(data))
        resp = json.loads(post_request.content)
        result = [{'id':resp['hits']['hits'][0]['_id'], 'value':'Did You Mean?'}]
    options = resp['hits']['hits']

    result_list = [{'id': i['_id'],
             'value': '{} | in brand {} | in category {}'.format(i['_source']['name'],
                                                          i['_source']['brand']['name'],
                                                          i['_source']['category']['name'])} for i in options]
    for item in result_list:
        result.append(item)

    data = json.dumps(result)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def product_detail(request):
    product_id = request.GET.get('product_id')
    product = Product.objects.get(pk=product_id)
    return render(request, 'sociolla/product-details.html', context={'product': product})


def search_result(request):
    query = request.GET.get('term', '')
    page = abs(int(request.GET.get('page', 1)))

    data = {
               "size": 10,
               "from": 10*(page-1),
               "query": {
                  "match": {
                     "_all": {
                        "query": query,
                        "operator": "and"
                     }
                  }
               }
            }
    resp = requests.post('http://localhost:9200/django/_search?pretty=true', json.dumps(data))
    resp = json.loads(resp.content)
    if resp['hits']['total'] == 0:
        data = {
                   "size": 10,
                   "from": 10*(page-1),
                   "query": {
                      "match": {
                         "_all": {
                            "query": query,
                            "operator": "or",
                            "analyzer": "filter_synonyms"
                         }
                      }
                   }
                }


        post_request = requests.post('http://localhost:9200/django/_search?pretty=true', json.dumps(data))
        resp = json.loads(post_request.content)
    options = resp['hits']['hits']

    data = [{'id': i['_id'],
          'name': i['_source']['name'],
          'brand': i['_source']['brand']['name'],
          'category': i['_source']['category']['name'],
          'description': i['_source']['description'],
          'price': i['_source']['price'],
          'image': i['_source']['image'],} for i in options]

    total_page = resp['hits']['total']/10+1

    return render(request, 'sociolla/search-result.html',
                  context={'data': data, 'page': page, 'total_page': total_page})
