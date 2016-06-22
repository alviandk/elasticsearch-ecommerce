from __future__ import unicode_literals

from django.db import models
from django.template.defaultfilters import slugify

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField()

    def save(self, *args, **kwargs):
        if self.id is None:
            self.slug = slugify(self.name)
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=128)
    banner = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    slug = models.SlugField()

    def save(self, *args, **kwargs):
        if self.id is None:
            self.slug = slugify(self.name)
        self.slug = slugify(self.name)
        super(Brand, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


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
