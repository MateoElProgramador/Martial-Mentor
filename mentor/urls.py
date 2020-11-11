from django.urls import path
from mentor import views

app_name = 'mentor'

urlpatterns = [
    path('', views.GameIndexView.as_view(), name='index'),
    path('game/<int:pk>', views.GameDetailView.as_view(), name='game_detail'),
]
