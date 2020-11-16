from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template.defaultfilters import register
from django.templatetags.static import static
from django.urls import reverse_lazy, reverse
from django.utils.safestring import mark_safe
from django.views import generic

from martialmentor.settings import STATIC_ROOT
from mentor.models import Game, UserCharacter


@register.filter(name='img_exists')
def img_exists(char):
    """Check whether file at given url exists, and return either original static filepath to file or placeholder img"""
    # Use STATIC_ROOT to check for file in correct absolute filepath:
    char_path = STATIC_ROOT + '/mentor/images/' + char.img_url()
    if default_storage.exists(char_path):
        # print(char_path, ' exists!')
        # print('Returning', static(char.rel_img_url()))
        return static(char.rel_img_url())
    else:
        # Return placeholder URL:
        # print(char_path, ' does not exist')
        new_filepath = '/mentor/images/char_placeholder.png'
        return static(new_filepath)


@register.filter(name='serve_char_img')
def serve_char_img(x):
    """ Create and return an img tag for the given character, the image url and CSS classes; depending
        on existence of character img and elite smash status."""
    char, elite_smash = x

    # Get img url (char or placeholder)
    # Elite smash check (grayscale)
    # Return complete img HTML tag

    img_url = img_exists(char)

    if elite_smash:
        grayscale_str = ''
    else:
        grayscale_str = ' grayscale'

    return mark_safe(
        '<img class="char_overlay_img img-fluid' + grayscale_str + '" src="' + img_url + '" alt="' + char.name + '">')


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

        # context['char_num'] = 4

        return context


def character_overlay(request, game_id):
    # If user not authenticated, redirect to login:
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    # Else get relevant data and serve overlay page:
    else:
        game = get_object_or_404(Game, pk=game_id)
        # __ syntax is used to reference attribute of foreign key:
        user_chars = UserCharacter.objects.filter(user=request.user, character__game=game)

        # count() is more efficient than len since the DB only returns the count and no objects:
        char_num = game.character_set.count()

        char_data = [0] * char_num
        i = 0

        # I'm probably hitting the database more than I need to here,
        # but I'll get it working first and optimise later.

        # Also I don't like having to make my own data structure when I already have 2 QuerySets,
        # but I can't see how else to do it without plaguing the template with logic.
        # TODO: Perf test, examine and optimise calls to database if required
        # TODO: Look into alternate manner of serving template with char and elite smash data
        for char in game.character_set.all():
            if user_chars.filter(character=char).exists() and user_chars.get(character=char).elite_smash == True:
                char_data[i] = (char, True)
            else:
                char_data[i] = (char, False)
            i += 1

        return render(request, 'mentor/char_overlay.html', {'game': game, 'user_chars': user_chars,
                                                            'char_num': char_num, 'char_data': char_data})


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form to include email address in fields."""

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class SignUpView(generic.CreateView):
    """Generic view for signing up."""
    form_class = CustomUserCreationForm  # get default form for signing up
    # reverse_lazy used due to generic class-based view
    # (URLconf won't yet be loaded):
    success_url = reverse_lazy('login')  # redirect to login upon successful signup
    template_name = 'registration/signup.html'
