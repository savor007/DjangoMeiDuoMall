import xadmin
from xadmin import views
from . import models
from celery_tasks.html.tasks import generate_static_category_list_html, generate_static_sku_detail_html

class SKUAdmin():
    model_icon='fa fa-gift'
    list_display=['id', 'name','price', 'stock', 'sales', 'comments']
    search_fields=['id', 'name']
    list_filter=['category','goods']
    list_editable=['price', 'stock']
    show_detail_fields=['name']
    show_bookmarks=True
    list_export=['xls','csv','xml']
    readonly_fields=['sales', "comments"]

    def save_models(self):
        object=self.new_obj
        object.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(object.id)


    def delete_model(self):
        object=self.obj
        sku_id=object.sku.id
        object.delete()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(object.id)


class SKUSpecificationAdmin():
    list_display = ['sku']
    list_editable = ['sku']
    def save_models(self):
        object=self.new_obj
        object.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(object.id)


    def delete_model(self):
        object=self.obj
        sku_id=object.sku.id
        object.delete()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(object.id)


class GoodsCategorySpeficationAdmin():
    def save_models(self):
        object = self.new_obj
        object.save()
        from celery_tasks.html.tasks import generate_static_category_list_html
        generate_static_category_list_html.delay(object.id)

    def delete_model(self):
        object = self.obj
        sku_id = object.sku.id
        object.delete()
        from celery_tasks.html.tasks import generate_static_category_list_html
        generate_static_category_list_html.delay(object.id)


class SKUImageAdmin():
    def save_models(self):
        object = self.new_obj
        object.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(object.id)



        sku=object.sku
        if not sku.default_image_url:
            sku.default_image_url=object.image.url
            sku.save()


    def delete_model(self):
        object = self.obj
        sku_id = object.id
        object.delete()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(sku_id )




xadmin.site.register(models.SKU, SKUAdmin)
xadmin.site.register(models.SKUSpecification, SKUSpecificationAdmin)
xadmin.site.register(models.GoodsCategory, GoodsCategorySpeficationAdmin)
xadmin.site.register(models.SKUImage,)
xadmin.site.register(models.Goods)