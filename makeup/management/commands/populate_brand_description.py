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

        brands = Brand.objects.all()

        for brand in brands:
            #try:
                url = brand.link
                r = requests.get(url, 'html.parser')
                content = BeautifulSoup(r.content)
                tab = content.find('div', {'id':'tab-2'})
                if not tab:
                    tab = content.find('div', {'id':'tab-1'})
                detail = tab.find('p')
                image = content.find('div', {'class':'brandbanner'}).find('img')
                brand.banner = image.get('src')
                brand.save()
                try:
                    brand.description = detail.text
                except:
                    pass
                brand.save()
                updated_records = updated_records + 1
                print 'brand updated {}'.format(updated_records)
            #except:
            #    not_updated = not_updated + 1
            #    print 'brand {} not updated: {}'.format(brand.id, not_updated)



        print updated_records
        print 'Finish'
