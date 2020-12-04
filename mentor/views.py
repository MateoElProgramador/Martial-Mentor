import json
from distutils.util import strtobool
from smashggAPI import client as sgg_client

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.defaultfilters import register
from django.templatetags.static import static
from django.urls import reverse_lazy, reverse
from django.utils.safestring import mark_safe
from django.views import generic

from martialmentor.settings import STATIC_ROOT, BASE_DIR
from mentor.models import Game, UserCharacter, snakify, Character


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
        print(char_path, ' does not exist')
        new_filepath = '/mentor/images/char_placeholder.png'
        return static(new_filepath)


@register.filter(name='serve_char_img')
def serve_char_img(x):
    """ Create and return an img tag for the given character, the image url and CSS classes; depending
        on existence of character img and elite smash status."""
    char, elite_smash = x
    s_name = snakify(char.name)

    # Get img url (char or placeholder)
    # Elite smash check (grayscale)
    # Return complete img HTML tag

    img_url = img_exists(char)

    if elite_smash:
        grayscale_str = ''
    else:
        grayscale_str = ' grayscale'

    return mark_safe(
        '<a href="' + reverse("mentor:elite_smash_toggle", args=[char.game.id]) + '?char_id=' + str(char.id) + '">'
            '<img id="' + snakify(char.name) + '" class="char_overlay_img img-fluid' + grayscale_str +
                    '" type="image" src="' + img_url + '" alt="' + char.name + '">'
        '</a>')


class GameIndexView(generic.ListView):
    model = Game
    template_name = 'mentor/index.html'


def tools(request, game_id):
    """Shows list of tools for selected game. Not that useful a page, will probably remove later."""
    game = get_object_or_404(Game, pk=game_id)
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
        list_77 = [0] * 77

        # Configure chroma key session:
        if request.session.get('chromakey') is None:
            request.session['chromakey'] = 'false'

        # Set values of body_class and checkbox_checked strings to display body and checkbox accordingly:
        if request.session['chromakey'] == 'true':
            body_class = 'chromakey'
            checkbox_checked = 'checked'
        else:
            body_class = ''
            checkbox_checked = ''

        # I'm probably hitting the database more than I need to here,
        # but I'll get it working first and optimise later.
        # Also I don't like having to make my own data structure when I already have 2 QuerySets,
        # but I can't see how else to do it without plaguing the template with logic.
        # TODO: Perf test, examine and optimise calls to database if required
        # TODO: Look into alternate manner of serving template with char and elite smash data
        i = 0
        for char in game.character_set.all():
            if user_chars.filter(character=char).exists() and user_chars.get(character=char).elite_smash is True:
                char_data[i] = (char, True)
            else:
                char_data[i] = (char, False)
            i += 1

        return render(request, 'mentor/char_overlay.html', {'game': game, 'user_chars': user_chars,
                                                            'char_num': char_num,
                                                            'char_data': char_data,
                                                            'body_class': body_class,
                                                            'checkbox_checked': checkbox_checked,
                                                            })
        # return render(request, 'mentor/[not used] example_char_overlay.html', {'game': game, 'user_chars': user_chars,
        #                                                     'char_num': char_num, 'char_data': char_data, 'list_77': list_77})


def elite_smash_toggle(request, game_id):
    """ Used as a go-between to easily send id of character clicked on char overlay, via anchor tag.
        Updates elite smash status of given character for signed in user, then redirects to character overlay page."""
    # If user not authenticated, redirect to login:
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    # Else get relevant data and serve overlay page:
    else:
        # Get UserCharacter record
        # If record doesn't exist, make one with elite_smash=True
        # Else toggle existing record
        # Toggle elite_smash

        # Get character:
        char = get_object_or_404(Character, pk=request.GET['char_id'])

        # Search for existing UserCharacter record for this user & char:
        user_char = UserCharacter.objects.filter(user=request.user, character=char).first()

        # If UserCharacter record doesn't exist, create new record:
        if user_char is None:
            UserCharacter.objects.create(user=request.user, character=char, elite_smash=True)
        # If record exists, toggle elite_smash boolean:
        else:
            elite_smash = user_char.elite_smash
            user_char.elite_smash = not elite_smash
            user_char.save()

        return HttpResponseRedirect(reverse('mentor:char_overlay', args=[game_id]))


def toggle_chromakey_session(request):
    """Receive Ajax requests which toggles chromakey session value."""
    if not request.is_ajax() or not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])

    # Toggle boolean by converting str to bool, inverting, then convert back to string:
    request.session['chromakey'] = str(not strtobool(request.session['chromakey'])).lower()
    print('chromakey session is now', request.session['chromakey'])
    return HttpResponse('ok')


# Insights:
def insights(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    print("Let's show some insights")

    # print('About to check that .env..')
    # env_dir = BASE_DIR + '\martialmentor\.env'
    # print('.env path:', env_dir)
    # load_dotenv(dotenv_path=env_dir)
    # print('API Key:', os.getenv('SMASHGG_API_KEY'))

    query = '''
        query TournamentQuery($slug: String, $perPage: Int) {
            tournament(slug: $slug){
                id
                name
                events {
                    id
                    name
            standings(query: {
              perPage: $perPage,
              page: 1
            }){
              nodes {
                placement
                entrant {
                  id
                  name
                }
              }
            }
                }
            }
        }'''
    query_vars = '{"slug": "cac-brac-all-stars-1", "perPage": 10} '
    # result = sgg_client.query(query, query_vars)
    # print(result)

    # -- Slugs to identify specific players: -- #
    # Mateo:
    user_slug = 'b1bbac32'
    # K.p:
    user_slug = '653c25e1'
    # Moo$:
    user_slug = 'a9b92e44'

    # Get player id and gamertag from user slug:
    user_player_query = '''
        query GetPlayerIdFromUserSlug($slug: String) {
          user(slug: $slug) {
            id
            player {
              id
              gamerTag
            }
          }
        }'''
    player_details = sgg_client.query(user_player_query, '{"slug": "'+user_slug+'"}')

    # Extract various IDs from player details query:
    player_id = player_details['data']['user']['player']['id']
    user_id = player_details['data']['user']['id']
    user_gamertag = player_details['data']['user']['player']['gamerTag']

    # Query for finding results of last 10 tournament sets of user, given user slug:
    recent_sets_query = '''
            query SetHistoryQuery($slug: String) {
                user(slug: $slug) {
                player {
                  gamerTag
                  sets(page: 1, perPage: 10) {
                    pageInfo {
                      total
                    }
                    nodes {
                      completedAt
                      displayScore
                      event {
                        tournament {
                          name
                        }
                      }
                      fullRoundText
                      lPlacement
                      winnerId
                      slots(includeByes: false) {
                        entrant{
                          id name
                        }
                      }
                    }
                  }
                }
              }
            }'''
    recent_sets_query_vars = '{"slug": "' + user_slug + '"}'

    # Get recent sets of given player:
    recent_sets_result = sgg_client.query(recent_sets_query, recent_sets_query_vars)

    i = 0

    # Find out whether given player was the winner in each set, and add 'win' key to each set entry:
    for p_set in recent_sets_result['data']['user']['player']['sets']['nodes']:
        print(p_set['winnerId'], ' VS ', player_id)

        # If entrant id of first entrant == winnerId, AND gamertag of first entrant == user_gamertag, then they won
        if (p_set['winnerId'] == p_set['slots'][0]['entrant']['id']) & (p_set['slots'][0]['entrant']['name'] == user_gamertag):
            p_set['win'] = 'true'
        # Same as above but in the event of the winner being the second listed entrant:
        elif (p_set['winnerId'] == p_set['slots'][1]['entrant']['id']) & (p_set['slots'][1]['entrant']['name'] == user_gamertag):
            p_set['win'] = 'true'
        else:
            p_set['win'] = 'false'

    # Put recent sets data into formatted string:
    recent_sets_result_str = json.dumps(recent_sets_result, indent=4)
    print(recent_sets_result_str)

    # Can't remember what this does, maybe convert string to JSON?
    # recent_sets_result_json = json.loads(recent_sets_result)

    return render(request, 'mentor/insights.html', {'game': game, 'recent_sets_result': recent_sets_result})


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
