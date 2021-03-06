import csv

from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify

from makeup.models import Brand

class Command(BaseCommand):
    args = 'file location'
    help = 'import brands'

    def handle(self, *args, **options):

        filename = args[0]

        csv_file = open(filename, 'rU')
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            slug = slugify(row['name'])
            try:
                brand = Brand.objects.get(slug=slug)
            except:
                brand = Brand.objects.create(name=row['name'])
            brand.link = row['link']
            brand.save()
