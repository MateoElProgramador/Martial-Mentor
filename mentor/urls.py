from django.urls import path
from mentor import views

app_name = 'mentor'

urlpatterns = [
    path('', views.index, name='index'),
]