import json
import requests

from elasticsearch.client import IndicesClient
from django.conf import settings
from django.core.management.base import BaseCommand
from makeup.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.recreate_index()

    def recreate_index(self):
        indices_client = IndicesClient(client=settings.ES_CLIENT)
        index_name = Product._meta.es_index_name
        if indices_client.exists(index_name):
            indices_client.delete(index=index_name)
        payload = {
           "settings": {
              "analysis": {
                 "filter": {
                    "nGram_filter": {
                       "type": "nGram",
                       "min_gram": 2,
                       "max_gram": 20,
                       "token_chars": [
                          "letter",
                          "digit",
                          "punctuation",
                          "symbol"
                       ]
                    },
                    "synonyms_filt" : {
                      "tokenizer": "keyword",
                        "type" : "synonym",
                        "synonyms_path" : "synonim.txt"
                    }
                 },
                 "analyzer": {
                    "nGram_analyzer": {
                       "type": "custom",
                       "tokenizer": "whitespace",
                       "filter": [
                          "lowercase",
                          "asciifolding",
                          "nGram_filter"
                       ]
                    },
                    "whitespace_analyzer": {
                       "type": "custom",
                       "tokenizer": "whitespace",
                       "filter": [
                          "lowercase",
                          "asciifolding"
                       ]
                    },
                    "filter_synonyms": {
                        "filter": [
                          "synonyms_filt"
                        ],
                        "tokenizer": "keyword"
                    }
                 }
              }
           },
           "mappings": {
             "product": {
                "_all": {
                   "analyzer": "nGram_analyzer",
                   "search_analyzer": "whitespace_analyzer"
                },
                "properties": {
                        'category': {
                            'type': 'object',
                            'properties': {
                                'name': {'type': 'string', 'index': 'not_analyzed'},
                            }
                        },
                        'brand': {
                            'type': 'object',
                            'properties': {
                                'name': {'type': 'string', 'index': 'not_analyzed'},
                            }
                        },
                        'name': {'type': 'string', 'index': 'not_analyzed'},
                        'price': {'type': 'long', "include_in_all": False, "index": "no"},
                        'description': {'type': 'string'},
                        'image': {'type': 'string', "include_in_all": False, "index": "no"},

                }
             }
          }
        }

        requests.post(settings.ES_URL, json.dumps(payload))
