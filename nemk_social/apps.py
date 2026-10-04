from django.apps import AppConfig
from django.contrib.admin import AdminSite


class NemkSocialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nemk_social'

    def ready(self):
        AdminSite.site_header = 'НЕМК Соціальна Мережа — Адміністрування'
        AdminSite.site_title = 'НЕМК Адмін'
        AdminSite.index_title = 'Панель управління'
