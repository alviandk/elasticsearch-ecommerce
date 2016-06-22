from django.contrib import admin

from makeup.models import Brand, Category, Product


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}

admin.site.register(Category, CategoryAdmin)
admin.site.register(Brand)
admin.site.register(Product)
