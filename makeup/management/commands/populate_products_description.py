import csv
import requests

from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify

from bs4 import BeautifulSoup

from makeup.models import Brand, Category, Product

class Command(BaseCommand):

    help = 'populate products description'

    def handle(self, *args, **options):

        #define basic parameters
        not_updated = 0
        updated_records = 0

        products = Product.objects.all()

        for product in products:
            try:
                url = product.link
                r = requests.get(url, 'html.parser')
                content = BeautifulSoup(r.content)
                detail = content.find('div', {'id':'Details'}).find('p')
                product.description = detail.text
                product.save()
                updated_records = updated_records + 1
                print 'product updated {}'.format(updated_records)
            except:
                not_updated = not_updated + 1
                print 'product {} not updated: {}'.format(product.id, not_updated)
                #product.delete()
                pass

        print updated_records
        print 'Finish'
