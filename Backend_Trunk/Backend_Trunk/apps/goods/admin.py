from django.contrib import admin
from . import models
from celery_tasks.html.tasks import generate_static_category_list_html, generate_static_sku_detail_html


class SKUAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        generate_static_sku_detail_html.delay(obj.id)


class SKUSpecificationAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        generate_static_sku_detail_html.delay(obj.sku.id)


    def delete_model(self, request, obj):
        sku_id=obj.sku.id
        obj.delete()
        generate_static_sku_detail_html(sku_id)



class SKUImageAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        generate_static_sku_detail_html.delay(obj.sku.id)

        sku=obj.sku
        if not sku.default_image_url:
            sku.default_image_url=obj.image.url
            sku.save()


    def delete_model(self, request, obj):
        sku_id=obj.sku.id
        obj.delete()
        generate_static_sku_detail_html(sku_id)


class GoodsCategoryAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        generate_static_category_list_html.delay()



    def delete_model(self, request, obj):
        sku_id=obj.sku.id
        obj.delete()
        generate_static_category_list_html.delay()




# Register your models here.
admin.site.register(models.GoodsCategory, GoodsCategoryAdmin)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Goods)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU, SKUAdmin)
admin.site.register(models.SKUSpecification, SKUSpecificationAdmin)
admin.site.register(models.SKUImage, SKUImageAdmin)