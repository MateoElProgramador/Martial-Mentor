from django.conf.urls.static import static
from django.urls import path

from martialmentor.settings import STATIC_URL, STATIC_ROOT
from mentor import views
from mentor.views import SignUpView, character_overlay, elite_smash_toggle

app_name = 'mentor'

urlpatterns = [
    path('', views.GameIndexView.as_view(), name='index'),
    path('game/', views.GameIndexView.as_view(), name='alt_index'),
    path('game/<int:game_id>/', views.tools, name='tools'),
    path('game/<int:game_id>/char-overlay/', character_overlay, name='char_overlay'),
    path('game/<int:game_id>/es-toggle', elite_smash_toggle, name='elite_smash_toggle'),
    path('signup/', SignUpView.as_view(), name='signup'),
]
