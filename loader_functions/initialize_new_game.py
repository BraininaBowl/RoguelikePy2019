import tcod as libtcod

from components.equipment import Equipment
from components.equippable import Equippable
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from components.graphics import tiles
from entity import Entity
from equipment_slots import EquipmentSlots
from game_messages import MessageLog
from game_states import GameStates
from map_objects.game_map import GameMap
from render_functions import RenderOrder

def get_constants():
    window_title = 'Rogue 451'
    screen_width = 120
    screen_height = 36

    # Messages panel
    panel_width = 30
    panel_height = screen_height
    panel_x = screen_width - panel_width

    message_x = 0
    message_width = panel_width - 3
    message_height = 800

    # Size of the map
    map_width = 80
    map_height = 40

    # Some variables for the rooms in the map
    room_max_size = 10
    room_min_size = 6
    max_rooms = 20

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    max_monsters_per_room = 3
    max_items_per_room = 2



    constants = {
        'window_title': window_title,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'panel_width': panel_width,
        'panel_height': panel_height,
        'panel_x': panel_x,
        'message_x': message_x,
        'message_width': message_width,
        'message_height': message_height,
        'map_width': map_width,
        'map_height': map_height,
        'room_max_size': room_max_size,
        'room_min_size': room_min_size,
        'max_rooms': max_rooms,
        'fov_algorithm': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius,
        'max_monsters_per_room': max_monsters_per_room,
        'max_items_per_room': max_items_per_room
    }

    return constants

def get_game_variables(constants):
    fighter_component = Fighter(hp=100, defense=1, power=2)
    inventory_component = Inventory(26)
    equipment_component = Equipment()
    level_component = Level()
    player = Entity(0, 0, tiles.get('player_tile'), libtcod.white, 'you', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, inventory=inventory_component, level=level_component,
                    equipment=equipment_component)
    entities = [player]

    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
#godmode    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=800, defense_bonus=800)
    dagger = Entity(0, 0, tiles.get('dagger_tile'), libtcod.white, 'Dagger', render_order=RenderOrder.ITEM, equippable=equippable_component, sprite_main_shift=320)
    player.inventory.add_item(dagger)
    player.equipment.toggle_equip(dagger)

    game_map = GameMap(constants['map_width'], constants['map_height'])
    game_map.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'],
                      constants['map_width'], constants['map_height'], player, entities)

    message_log = MessageLog(constants['message_x'], constants['message_width'], constants['message_height'])

    game_state = GameStates.PLAYERS_TURN

    return player, entities, game_map, message_log, game_state