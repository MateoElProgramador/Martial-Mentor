from django.contrib.auth.forms import UserCreationForm
from django.core.files.storage import default_storage
from django.shortcuts import render
from django.template.defaultfilters import register
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.views import generic

from martialmentor.settings import STATIC_ROOT
from mentor.models import Game


@register.filter(name='img_exists')
def img_exists(filepath):
    """Check whether file at given url exists, and return either original static filepath to file or placeholder img"""
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


def tools(request, game_id):
    """Shows list of tools for selected game. Not that useful a page, will probably remove later."""
    game = Game.objects.get(pk=game_id)
    return render(request, 'mentor/tools.html', {'game': game})


class GameDetailView(generic.DetailView):
    """Used for character overlay."""
    model = Game
    template_name = 'mentor/char_overlay.html'

    def get_context_data(self, **kwargs):
        """Override get context method to add variable to context."""
        context = super().get_context_data(**kwargs)
        # context['list_60'] = 'a' * 60
        # context['list_17'] = 'a' * 17
        # context['list_77'] = 'a' * 77

        game = self.object
        char_num = len(game.character_set.all())
        print('Character num: ', char_num)

        context['char_num'] = char_num

        # context['char_num'] = 77

        return context


class SignUpView(generic.CreateView):
    """Generic view for signing up."""
    form_class = UserCreationForm       # get default form for signing up
    # reverse_lazy used due to generic class-based view
    # (URLconf won't yet be loaded):
    success_url = reverse_lazy('login')     # redirect to login upon successful signup
    template_name = 'registration/signup.html'
