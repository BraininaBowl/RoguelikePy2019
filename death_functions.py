import tcod as libtcod

from components.graphics import colors
from game_messages import Message
from render_functions import RenderOrder
from game_states import GameStates


def kill_player(player):
    #player.char = '%'
    #player.color = colors.get('dark')
    return Message('You died!', colors.get('light')), GameStates.PLAYER_DEAD



def kill_monster(monster):
    death_message = Message('{0} is dead!'.format(monster.name.capitalize()), colors.get('green'))

#    monster.color = colors.get('dark')
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.render_order = RenderOrder.CORPSE

    return death_message