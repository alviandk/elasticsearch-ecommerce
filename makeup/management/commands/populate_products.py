import csv

from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify

from makeup.models import Brand, Category, Product

class Command(BaseCommand):
    args = 'file location, product_category slug'
    help = 'import categories'

    def handle(self, *args, **options):

        #define basic parameters
        total_records = 0
        updated_records = 0
        created_records = 0

        filename = args[0]
        category_slug = slugify(args[1])
        delimiter = options.get('delimiter',',')

        csv_file = open(filename, 'rU')
        csv_reader = csv.DictReader(csv_file)

        category = Category.objects.get(slug=category_slug)

        for row in csv_reader:
            brand_slug = slugify(row['brand'])
            brand = Brand.objects.get(slug=brand_slug)
            product_name = row['name']
            try:
                product = Product.objects.get(name=product_name, brand=brand)
            except:
                product = Product(name=product_name, brand=brand)
                product.category = category
                product.image = row['image']
                product.link = row['link']
                product.price = row['price']
                product.save()
                created_records = created_records + 1
                print 'product created {}'.format(created_records)


        print created_records
        print 'Finish'
