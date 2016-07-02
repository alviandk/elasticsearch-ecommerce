from django.conf import settings
from django.core.management.base import BaseCommand

from elasticsearch.client import IndicesClient
from elasticsearch.helpers import bulk

from makeup.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.push_db_to_index()

    def push_db_to_index(self):
        data = [
            self.convert_for_bulk(s, 'create') for s in Product.objects.all()
        ]
        bulk(client=settings.ES_CLIENT, actions=data, stats_only=True)

    def convert_for_bulk(self, django_object, action=None):
        data = django_object.es_repr()
        metadata = {
            '_op_type': action,
            "_index": django_object._meta.es_index_name,
            "_type": django_object._meta.es_type_name,
        }
        data.update(**metadata)
        return data
