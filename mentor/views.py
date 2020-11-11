from django.shortcuts import render
from django.views import generic
from mentor.models import Game


class GameIndexView(generic.ListView):
    model = Game
    template_name = 'mentor/index.html'


class GameDetailView(generic.DetailView):
    model = Game
    template_name = 'mentor/game_detail.html'
