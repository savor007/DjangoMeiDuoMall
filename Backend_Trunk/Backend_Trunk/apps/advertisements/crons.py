from collections import OrderedDict     #默认字典是无序的， OderedDict 提供有序字典
from django.conf import settings
from django.template import loader
import os
import time
import logging

from goods.models import GoodsChannel
from .models import ContentCategory

logger=logging.getLogger('django')

def generate_static_index_html():
    logger.info(time.ctime())

    categories = OrderedDict()
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    for channel in channels:
        group_id = channel.group_id  # 当前组

        if group_id not in categories:
            categories[group_id] = {'channels': [], 'sub_cats': []}

        cat1 = channel.category  # 当前频道的类别

        # 追加当前频道
        categories[group_id]['channels'].append({
            'id': cat1.id,
            'name': cat1.name,
            'url': channel.url
        })
        # 构建当前类别的子类别
        for cat2 in cat1.goodscategory_set.all():
            cat2.sub_cats = []
            for cat3 in cat2.goodscategory_set.all():
                cat2.sub_cats.append(cat3)
            categories[group_id]['sub_cats'].append(cat2)

    #  sub_cats 指向三级，最底层菜单

    # 广告内容
    contents = {}
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

    # 渲染模板
    context = {
        'categories': categories,
        'contents': contents
    }
    template = loader.get_template('index.html')
    html_text = template.render(context)
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'index.html')
    with open(file_path, 'w') as f:
        f.write(html_text)

