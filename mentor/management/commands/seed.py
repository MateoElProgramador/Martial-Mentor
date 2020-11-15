from django.core.management.base import BaseCommand
from mentor.models import Character, Game

ssbu_chars = ['Mario', 'Donkey Kong', 'Link', 'Samus', 'Dark Samus', 'Yoshi',
              'Kirby', 'Fox', 'Pikachu', 'Luigi', 'Ness', 'Captain Falcon',
              'Jigglypuff', 'Peach', 'Daisy', 'Bowser', 'Ice Climbers', 'Sheik',
              'Zelda', 'Dr. Mario', 'Pichu', 'Falco', 'Marth', 'Lucina',
              'Young Link', 'Ganondorf', 'Mewtwo', 'Roy', 'Chrom',
              'Mr. Game & Watch', 'Meta Knight', 'Pit', 'Dark Pit',
              'Zero Suit Samus', 'Wario', 'Snake', 'Ike', 'Pokémon Trainer',
              'Diddy Kong', 'Lucas', 'Sonic', 'King Dedede', 'Olimar', 'Lucario',
              'R.O.B.', 'Toon Link', 'Wolf', 'Villager', 'Mega Man',
              'Wii Fit Trainer', 'Rosalina & Luma', 'Little Mac', 'Greninja',
              'Palutena', 'Pac-Man', 'Robin', 'Shulk', 'Bowser Jr.',
              'Duck Hunt Duo', 'Ryu', 'Ken', 'Cloud', 'Corrin', 'Bayonetta',
              'Inkling', 'Ridley', 'Simon', 'Richter', 'King K. Rool',
              'Isabelle', 'Incineroar', 'Piranha Plant', 'Joker', 'Hero',
              'Banjo & Kazooie', 'Terry', 'Byleth', 'Min Min', 'Steve',
              'Mii Brawler', 'Mii Swordfighter', 'Mii Gunner']


class Command(BaseCommand):
    help = "seed database for testing and development."

    def add_arguments(self, parser):
        parser.add_argument('--mode', type=str, help="Mode")

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        run_seed(self, options['mode'])
        self.stdout.write('done.')


def clear_data():
    Game.objects.all().delete()


def populate_tables():
    # Create game:
    ssbu = Game.objects.create(title='Super Smash Bros. Ultimate', short_title='Smash Ultimate')
    ssbu.save()

    # Populate characters:
    for char in ssbu_chars:
        c = Character(name=char, game=ssbu)
        c.save()


def run_seed(self, mode):
    clear_data()
    populate_tables()
