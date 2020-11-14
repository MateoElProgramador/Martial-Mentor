from django.urls import path
from mentor import views
from mentor.views import SignUpView

app_name = 'mentor'

urlpatterns = [
    path('', views.GameIndexView.as_view(), name='index'),
    path('game/', views.GameIndexView.as_view(), name='alt_index'),
    path('game/<int:game_id>/', views.tools, name='tools'),
    path('game/<int:pk>/char-overlay/', views.GameDetailView.as_view(), name='char_overlay'),
    path('signup/', SignUpView.as_view(), name='signup'),
]
