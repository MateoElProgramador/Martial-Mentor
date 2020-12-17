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

    def get_context_data(self, **kwargs):
        """Override get context method to add variables to context."""
        context = super().get_context_data(**kwargs)
        context['all_games'] = Game.objects.all()
        return context


def tools(request, game_id):
    """Shows list of tools for selected game. Not that useful a page, will probably remove later."""
    game = get_object_or_404(Game, pk=game_id)
    all_games = Game.objects.all()
    return render(request, 'mentor/tools.html', {'game': game, 'all_games': all_games})


class GameDetailView(generic.DetailView):
    """Used for character overlay."""
    model = Game
    template_name = 'mentor/char_overlay.html'

    def get_context_data(self, **kwargs):
        """Override get context method to add variable to context."""
        context = super().get_context_data(**kwargs)
        # context['list_77'] = 'a' * 77

        game = self.object
        char_num = len(game.character_set.all())
        print('Character num: ', char_num)

        context['char_num'] = char_num
        context['all_games'] = Game.objects.all()

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
                                                            'all_games': Game.objects.all(),
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
    opponent_slug = ''

    if request.method == "POST":
        user_slug = request.POST['slug1']
        # Get slug of opponent if not blank:
        if request.POST['slug2']:
            opponent_slug = request.POST['slug2']

    else:
        # -- Slugs to identify specific players: -- #
        # Mateo:
        user_slug = 'b1bbac32'
        # K.p:
        user_slug = '653c25e1'
        # Hungrybox:
        user_slug = '076502c1'
        # Moo$:
        user_slug = 'a9b92e44'

    return render(request, 'mentor/insights.html', {'game': game, 'method': request.method, 'user_slug': user_slug,
                                                    'opponent_slug': opponent_slug, 'all_games': Game.objects.all()})


def recent_sets_async(request):
    """Get recent sets of given player using the smashgg API. Called by Ajax."""
    if not request.is_ajax() or not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])

    game = get_object_or_404(Game, pk=request.POST['game_id'])
    user_slug = request.POST['user_slug']

    print("Recent sets async")
    # print(request.POST)

    # Get slug of opponent if not blank:
    if ('slug2' in request.POST) and request.POST['slug2']:
        opponent_slug = request.POST['slug2']
        # set_num = 100
    else:
        opponent_slug = ''
        # set_num = 80

    page_num = request.POST['page_num']
    per_page = request.POST['per_page']

    # print('Page', page_num)

    # Query for finding results of last 10 tournament sets of user, given user slug:
    recent_sets_query = '''
                query RecentSetsQuery($slug: String, $page: Int, $perPage: Int) {
                    user(slug: $slug) {
                    player {
                      gamerTag
                      sets(page: $page, perPage: $perPage, filters: {
                        hideEmpty: true
                      }) {
                        pageInfo {
                          total
                        }
                        nodes {
                          id
                          completedAt
                          displayScore
                          event {
                            videogame {
                              name
                            }
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
    recent_sets_query_vars = '{"slug": "' + user_slug + '", "page": "' + str(page_num) + '", "perPage": "' + str(per_page) + '"}'

    # Get recent sets of given player:
    recent_sets = sgg_client.query(recent_sets_query, recent_sets_query_vars)['data']['user']

    # If user key points to null, then player slug doesn't exist; return blank data:
    if recent_sets is None:
        print('User is null!')
        return HttpResponse(json.dumps({'recent_sets': 'null'}))

    recent_sets = recent_sets['player']

    user_gamertag = recent_sets['gamerTag']

    i = 0
    del_inds = []
    win_count = 0

    # Find out whether given player was the winner in each set, and add 'win' key to each set entry:
    for i, p_set in enumerate(recent_sets['sets']['nodes']):

        # Collate indices of sets not for this game:
        if p_set['event']['videogame']['name'] != game.title:
            # print(p_set['event']['tournament']['name'], 'is not', game.title, ', it is', p_set['event']['videogame']['name'])
            del_inds.append(i)
            continue

        # If set is a DQ (disqualification), or displayScore is null, then mark this index for deletion:
        if p_set['displayScore'] == 'DQ' or not p_set['displayScore']:
            # print('Set', i, 'is a DQ/ null displayScore')
            del_inds.append(i)
            continue

        # If entrant id of first entrant == winnerId, AND user gamertag is substring of first entrant, then they won
        # Note: Checking that user_gamertag is in entrant name is to avoid discrepancies between gamertags from user
        # not containing sponsors, e.g. 'Hungrybox' and 'Liquid | Hungrybox. This could cause issues if one player's
        # gamertag was a substring of their opponent's...
        # TODO: Come up with more robust way of identifying winner
        if (p_set['winnerId'] == p_set['slots'][0]['entrant']['id']) & (
                user_gamertag in p_set['slots'][0]['entrant']['name']):
            p_set['win'] = 'true'
            win_count += 1
        # Same as above but in the event of the winner being the second listed entrant:
        elif (p_set['winnerId'] == p_set['slots'][1]['entrant']['id']) & (
                user_gamertag in p_set['slots'][1]['entrant']['name']):
            p_set['win'] = 'true'
            win_count += 1
        else:
            p_set['win'] = 'false'

    # Add win count to dictionary:
    recent_sets['winCount'] = win_count

    # Filter out sets not for this videogame:
    recent_sets['sets']['nodes'] = \
        [elem for i, elem in enumerate(recent_sets['sets']['nodes'])
         if i not in del_inds]

    # recent_sets['sets']['nodes'] = recent_sets['sets']['nodes'][:15]        # Cap displayed sets to 15

    # print(json.dumps(recent_sets, indent=4))
    response = {'recent_sets': recent_sets}
    return HttpResponse(json.dumps(response))


def user_details_async(request):
    """Get user details given user slug in request. Called by Ajax."""
    if not request.is_ajax() or not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])

    user_slug = request.POST['user_slug']
    # Get user details using helper method:
    user_details = get_user_details(user_slug)

    # If query doesn't find user, then flag as null in response JSON:
    if user_details is None:
        user_details = 'null'

    response = {'user_details': user_details}
    return HttpResponse(json.dumps(response))


def get_user_details(user_slug):
    """Uses smash.gg API to get and return user details given a user slug."""
    # Get player id and gamertag from user slug:
    user_player_query = '''
            query GetUserDetails($slug: String) {
              user(slug: $slug) {
                id
                player {
                  id
                  gamerTag
                }
              }
            }'''
    user_details = sgg_client.query(user_player_query, '{"slug": "' + user_slug + '"}')['data']['user']
    return user_details


def recent_placements_async(request):
    """Get recent tournament placements of given player using the smashgg API. Called by Ajax."""
    if not request.is_ajax() or not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])

    game = get_object_or_404(Game, pk=request.POST['game_id'])
    user_slug = request.POST['user_slug']
    user_gamertag = request.POST['user_gamertag']

    # Hardcoded list of videogame IDS:
    videogame_ids = {'Super Smash Bros. Ultimate': 1386, 'Super Smash Bros. Melee': 1}

    # Get player's placements of 10 most recent tournaments:
    recent_placements_query = '''query GetPlayerPlacements($slug: String, $gamertag: String, $videogameId: ID!) {
              user(slug: $slug) {
                    events(query: {
                  page: 1,
                  perPage: 15,
                  filter: {
                    videogameId: [$videogameId]
                  }
                }) {
                  nodes {
                  name
                  slug
                  videogame {
                    name
                  }
                    tournament {
                      name
                    }
                    numEntrants
                    standings(query: {
                      filter: {
                        search: {
                          fieldsToSearch: "gamerTag"
                          searchString: $gamertag
                        }
                      }
                    }) {
                      nodes {
                        placement
                      }
                    }
                  }
                }
              }
            }'''
    recent_placements_vars = '{"slug": "' + user_slug + '", "gamertag": "' + user_gamertag + '", "videogameId": "' + str(videogame_ids[game.title]) + '"}'
    recent_placements = sgg_client.query(recent_placements_query, recent_placements_vars)['data']['user']['events']['nodes']

    # print(json.dumps(recent_placements, indent=4))

    del_inds = []

    # Calculate top percentage based on tournament placements, and add to dict:
    for i, placement in enumerate(recent_placements):
        print(placement, '\n\n')

        # Deal with tournaments where standings are null:
        if not placement['standings']:
            print('Null alert!')
            placement['topPerc'] = 'null'
            continue
            # del_inds.append(i)
        # If the standings is not null but the nodes is, then the player dropped out and didn't compete:
        elif not placement['standings']['nodes']:
            print('Did not compete!')
            placement['topPerc'] = 'did not compete'
            # del_inds.append(i)
        else:
            placement['topPerc'] = round((placement['standings']['nodes'][0]['placement'] / placement['numEntrants']) * 100)

    # Filter out placements not for this videogame:
    # recent_placements = [elem for i, elem in enumerate(recent_placements) if i not in del_inds]
    # recent_placements = recent_placements[:10]       # Cap number of placements displayed

    response = {'placements': recent_placements}
    return HttpResponse(json.dumps(response))


def set_history_async(request):
    """Get set history between two players, given both user slugs. Called by Ajax."""
    if not request.is_ajax() or not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])

    game = get_object_or_404(Game, pk=request.POST['game_id'])
    user_slug = request.POST['user_slug']
    opponent_slug = request.POST['opponent_slug']
    user_gamertag = request.POST['user_gamertag']
    opponent_gamertag = request.POST['opponent_gamertag']

    sets = json.loads(request.POST['sets'])

    # Get user details of opponent:
    # opponent_details = get_user_details(opponent_slug)

    # If no user found for opponent slug, then return null value in JSON:
    # if opponent_details is None:
    #     return HttpResponse(json.dumps({'set_history': 'null'}))

    # opponent_id = opponent_details['player']['id']
    # opponent_gamertag = opponent_details['player']['gamerTag']

    # NOTE: This query should filter sets to find set history between 2 players, but there's a bug
    # in the API and it's broken...
    set_history_query = '''
        query GetSetHistory($slug1: String, $opp_id: ID!){
          user(slug: $slug1) {
            player {
              sets(filters: {
                playerIds: [$opp_id]
              }) {
                pageInfo {
                  total,
                  totalPages,
                  sortBy,
                  filter,
                  page,
                  perPage
                }
                nodes {
                  id
                }
              }
            }
          }
        }'''

    # set_history_vars = '{"slug1": "' + user_slug + '", "opp_id": ' + int(opponent_id) + '}'
    # set_history = sgg_client.query(set_history_query, set_history_vars)

    # set_hist_inds = []
    win_count = 0
    set_history = {'opponentGamertag': opponent_gamertag, 'winCount': 0, 'sets': []}

    print(json.dumps(sets, indent=4))
    print('Total sets for this game:', len(sets))
    print('Opponent gamertag:', opponent_gamertag)

    # Filter sets which contain opponent:
    for i, p_set in enumerate(sets):
        if (opponent_gamertag in p_set['slots'][0]['entrant']['name']) or (opponent_gamertag in p_set['slots'][1]['entrant']['name']):
            # set_hist_inds.append(i)
            print('Aha!')
            set_history['sets'].append(p_set)
            if p_set['win'] == 'true':
                win_count += 1

    set_history['winCount'] = win_count

    print(set_history)

    response = {'set_history': set_history}
    # print(json.dumps(response, indent=4))
    return HttpResponse(json.dumps(response))


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
