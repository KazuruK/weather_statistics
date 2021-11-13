from django.urls import path

from . import views

app_name = "stats"

urlpatterns = [
    path('load_data/', views.load_data, name='load_data'),
    path('', views.index, name='index'),
]
