import django.db.models.options as options

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.template.defaultfilters import slugify

import django.db.models.options as options
options.DEFAULT_NAMES = options.DEFAULT_NAMES + (
    'es_index_name', 'es_type_name', 'es_mapping'
)
es_client = settings.ES_CLIENT

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField()

    def save(self, *args, **kwargs):
        if self.id is None:
            self.slug = slugify(self.name)
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)
        for product in self.product_category.all():
            data = product.field_es_repr('category')
            es_client.update(
                index=product._meta.es_index_name,
                doc_type=product._meta.es_type_name,
                id=product.pk,
                body={
                    'doc': {
                        'category': data
                    }
                }
            )

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=128)
    banner = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    slug = models.SlugField()

    def __str__(self):
        return self.name

'''
    def save(self, *args, **kwargs):
        if self.id is None:
            self.slug = slugify(self.name)
        self.slug = slugify(self.name)
        super(Brand, self).save(*args, **kwargs)
        for product in self.product_brand.all():
            data = product.field_es_repr('brand')
            es_client.update(
                index=product._meta.es_index_name,
                doc_type=product._meta.es_type_name,
                id=product.pk,
                body={
                    'doc': {
                        'brand': data
                    }
                }
            )
'''


class Product(models.Model):
    name = models.CharField(max_length=128)
    image = models.URLField()
    brand = models.ForeignKey(Brand, related_name='product_brand')
    link = models.URLField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, related_name='product_category')
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        es_index_name = 'django'
        es_type_name = 'product'
        es_mapping = {
            'properties': {
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
                'price': {'type': 'long'},
                'description': {'type': 'string'},
                'name_complete': {
                    'type': 'completion',  # you have to make a method for completition for sure!
                    'analyzer': 'simple',
                    'payloads': True,  # note that we have to provide payload while updating
                    'preserve_separators': True,
                    'preserve_position_increments': True,
                    'max_input_length': 50,
                },
            }
        }

    def es_repr(self):
        data = {}
        mapping = self._meta.es_mapping
        data['_id'] = self.pk

        for field_name in mapping['properties'].keys():
            data[field_name] = self.field_es_repr(field_name)
        return data

    def field_es_repr(self, field_name):
        config = self._meta.es_mapping['properties'][field_name]
        if hasattr(self, 'get_es_%s' % field_name):
            field_es_value = getattr(self, 'get_es_%s' % field_name)()
        else:
            if config['type'] == 'object':
                related_object = getattr(self, field_name)
                field_es_value = {}
                field_es_value['_id'] = related_object.pk
                for prop in config['properties'].keys():
                    field_es_value[prop] = getattr(related_object, prop)
            else:
                field_es_value = getattr(self, field_name)
        return field_es_value

    def get_es_name_complete(self):
        return {
            "input": [self.name],
            "output": self.name,
            "payload": {"pk": self.pk},
        }

    def get_es_brand_names(self):
        if not self.brand.exists():
            return []
        return [c.name for c in self.brand.all()]

    def save(self, *args, **kwargs):
        is_new = self.pk
        super(Product, self).save(*args, **kwargs)
        payload = self.es_repr()
        if is_new is not None:
            del payload['_id']
            es_client.update(
                index=self._meta.es_index_name,
                doc_type=self._meta.es_type_name,
                id=self.pk,
                refresh=True,
                body={
                    'doc': payload
                }
            )
        else:
            es_client.create(
                index=self._meta.es_index_name,
                doc_type=self._meta.es_type_name,
                id=self.pk,
                refresh=True,
                body={
                    'doc': payload
                }
            )

    def delete(self, *args, **kwargs):
        prev_pk = self.pk
        super(Product, self).delete(*args, **kwargs)
        es_client.delete(
            index=self._meta.es_index_name,
            doc_type=self._meta.es_type_name,
            id=prev_pk,
            refresh=True,
        )
