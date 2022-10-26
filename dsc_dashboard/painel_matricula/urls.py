from django.urls import path
from . import views
from .dashboards import dashboard

app_name = 'painel_matricula'
urlpatterns = [
    path('', views.index, name='index'),
]
