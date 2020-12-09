from django.conf.urls.static import static
from django.urls import path

from martialmentor.settings import STATIC_URL, STATIC_ROOT
from mentor import views
from mentor.views import SignUpView, character_overlay, elite_smash_toggle, toggle_chromakey_session, insights, \
    recent_sets_async, recent_placements_async, user_details_async, set_history_async

app_name = 'mentor'

urlpatterns = [
    path('', views.GameIndexView.as_view(), name='index'),
    path('game/', views.GameIndexView.as_view(), name='alt_index'),
    path('game/<int:game_id>/', views.tools, name='tools'),

    # Character overlay:
    path('game/<int:game_id>/char-overlay/', character_overlay, name='char_overlay'),
    path('toggle_chromakey/', toggle_chromakey_session, name='toggle_chromakey'),       # Ajax chromakey session toggle
    path('game/<int:game_id>/es-toggle/', elite_smash_toggle, name='elite_smash_toggle'),

    # Insights:
    path('game/<int:game_id>/insights/', insights, name='insights'),
    # Insights paths used by Ajax to fetch data:
    path('get-user-details/', user_details_async),
    path('get-recent-sets/', recent_sets_async),
    path('get-recent-placements/', recent_placements_async),
    path('get-set-history/', set_history_async),

    path('signup/', SignUpView.as_view(), name='signup'),
]
