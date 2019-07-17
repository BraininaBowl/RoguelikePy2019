import tcod as libtcod

from components.graphics import colors
from game_messages import Message


def heal(*args, **kwargs):
    entity = args[0]
    amount = kwargs.get('amount')

    results = []

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append({'consumed': False, 'message': Message('You are already at full health', colors.get('dark'))})
    else:
        entity.fighter.heal(amount)
        results.append({'consumed': True, 'message': Message('Your wounds start to feel better!', colors.get('green'))})

    return results