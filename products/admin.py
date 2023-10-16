from django.contrib import admin

from .models import (
    Product,
    ProductProperties,
    ProductImages,
    ProductEquipments,
    ProductDescriptions,
)


admin.site.register(Product)
admin.site.register(ProductProperties)
admin.site.register(ProductImages)
admin.site.register(ProductEquipments)
admin.site.register(ProductDescriptions)