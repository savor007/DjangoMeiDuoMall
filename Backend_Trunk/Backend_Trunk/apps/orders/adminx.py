import xadmin
from xadmin import views
from . import models

class OrderAdmin():
    list_display=['order_id','create_time','total_amount','total_count', 'pay_method', 'status']
    refresh_times=[2, 10]   # 可以选择支持按多长时间内间隔刷新页面
    data_charts={
      "order_amount":{'title':"订单金额","x-field":"create_time", "y-field":("total_amount",), "order":("create_time",)},
        "order_count":{'title':"订单数量","x-field":"create_time","y-field":("total_count",), "order":("create_time",)}
    }
    readonly_fields=['total_amount', "total_count"]

xadmin.site.register(models.OrderInfo, OrderAdmin)