from django.urls import path
from . import views
from .dashboards.apps import app_1, app_2, app_3, app_4, app_5, app_6


app_name = 'dashboards'
urlpatterns = [
    path('', views.app_1, name='diretoria'),
    path('diretoria', views.app_1, name='diretoria'),
    path('conectividade', views.app_2, name='conectividade'),
    path('sistemas', views.app_3, name='sistemas'),
    path('servicos', views.app_4, name='servicos'),
    path('micro', views.app_5, name='micro'),
    path('suporte', views.app_6, name='suporte'),
]
