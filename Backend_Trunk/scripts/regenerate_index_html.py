#!/usr/bin/env python3
"""
功能：手动生成首页index.html静态文件， 使用方法 ./regenerate_index_html.py
"""
import sys
sys.path.insert(0, '../')
sys.path.insert(0,'../Backend_Trunk/apps')


import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE']='Backend_Trunk.settings.DevelopmentSettings'


"""
让Django进行初始化
"""
import django
django.setup()


from advertisements.crons import generate_static_index_html


if __name__ == '__main__':
    generate_static_index_html()
