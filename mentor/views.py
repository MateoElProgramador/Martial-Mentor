from django.core.files.storage import default_storage
from django.shortcuts import render
from django.template.defaultfilters import register
from django.templatetags.static import static
from django.views import generic

# from martialmentor.settings import STATIC_ROOT
from martialmentor.settings import STATIC_ROOT
from mentor.models import Game


# TODO: Figure out how to handle static files properly
# --- Not currently used: ---
@register.filter(name='file_exists')
def file_exists(filepath):
    # Use STATIC_ROOT to check for file in correct absolute filepath:
    if default_storage.exists(STATIC_ROOT + '/static/' + filepath):
        return static(filepath)
    else:
        # Return placeholder URL:
        new_filepath = '/mentor/images/char_placeholder.jpg'
        return static(new_filepath)


class GameIndexView(generic.ListView):
    model = Game
    template_name = 'mentor/index.html'


class GameDetailView(generic.DetailView):
    model = Game
    template_name = 'mentor/game_detail.html'
