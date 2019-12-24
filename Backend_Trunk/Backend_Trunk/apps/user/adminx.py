import xadmin
from xadmin import views
from . import models
from xadmin.plugins import auth

class BaseSettings(object):
    """
    xadmin的基本配置
    """
    enable_themes=True    #开启主题切换功能
    use_bootswatch=True   #

xadmin.site.register(views.BaseAdminView, BaseSettings)

class GlobalSettings(object):
    """
    设置xadmin的全局配置
    """
    site_title="美多商城运营管理系统"   #设置站点标题
    site_footer="Meiduo Cooperation" #  设置站点的页脚
    menu_style="accordion"    #设置菜单折叠显示


class UserAdmin(auth.UserAdmin):
    list_display = ['id','username','mobile', 'email','date_joined']
    readonly_fields=['last_login', 'date_joined']
    search_fields = ['username','first_name','last_name','email','mobile']
    style_fields = {'user_permissions':'m2m_transfer', 'groups':'m2m_transfer'}
    """
    style是指组设定
    """

    def get_model_form(self, **kwargs):
        if self.org_obj is None:
            """
            意味着新增一个user, 利用这个机会增加mobile
            """
            self.fields=['username','mobile','is_staff']
        return super().get_model_form(**kwargs)


xadmin.site.register(views.CommAdminView, GlobalSettings)
xadmin.site.unregister(models.User)
xadmin.site.register(models.User, UserAdmin)

