import tcod as libtcod

from components.graphics import colors, tiles
from enum import Enum
from game_states import GameStates
from menus import inventory_menu

class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3

def get_names_under_mouse(cam_x,cam_y,mouse, entities, fov_map):
    (x, y) = (mouse.cx+cam_x, mouse.cy+cam_y)

    names = [entity.name for entity in entities
             if (entity.x*2 == x or entity.x*2+1 == x) and (entity.y*2 == y or entity.y*2+1 == y) and libtcod.map_is_in_fov(fov_map, entity.x, entity.y)]
    names = ', '.join(names)
    return names.capitalize()

def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color, text_color):
    bar_width = int(float(value) / maximum * total_width)

    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SET)

    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SET)

    libtcod.console_set_default_foreground(panel, text_color)
    libtcod.console_print_ex(panel, int(x + total_width / 2), y, libtcod.BKGND_NONE, libtcod.CENTER, '{0}: {1}/{2}'.format(name, value, maximum))

def render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, screen_height, map_width, map_height, bar_width, panel_height, panel_y, mouse, colors, cam_x, cam_y,anim_frame, game_state):

    libtcod.console_clear(0)

    if fov_recompute:
        # Draw all the tiles in the game map
        libtcod.console_set_default_foreground(con, libtcod.white)
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight
                if visible:
                    if game_state == GameStates.TARGETING and mouse.distance(x, y) <= radius:
                        backcolor = colors.get('red')
                    else:
                        backcolor = colors.get('light')
                else:
                    backcolor = colors.get('dark')


                if visible:
                    if game_state == GameStates.TARGETING and mouse.distance(x,y) <= radius:
                        libtcod.console_set_char_background(con, x * 2, y * 2, colors.get('red'), libtcod.BKGND_SET)
                        libtcod.console_set_char_background(con, x * 2 + 1, y * 2, colors.get('red'), libtcod.BKGND_SET)
                        libtcod.console_set_char_background(con, x * 2, y * 2 + 1, colors.get('red'), libtcod.BKGND_SET)
                        libtcod.console_set_char_background(con, x * 2 + 1, y * 2 + 1, colors.get('red'), libtcod.BKGND_SET)
                    else:
                        libtcod.console_set_char_background(con, x * 2, y * 2, colors.get('light'), libtcod.BKGND_SET)
                        libtcod.console_set_char_background(con, x * 2 + 1, y * 2, colors.get('light'), libtcod.BKGND_SET)
                        libtcod.console_set_char_background(con, x * 2, y * 2 + 1, colors.get('light'), libtcod.BKGND_SET)
                        libtcod.console_set_char_background(con, x * 2 + 1, y * 2 + 1, colors.get('light'), libtcod.BKGND_SET)

                    if wall:
                        libtcod.console_put_char(con, x*2, y*2, tiles.get('wall_tile'), libtcod.BKGND_NONE)
                        libtcod.console_put_char(con, x*2+1, y*2, tiles.get('wall_tile')+1, libtcod.BKGND_NONE)
                        libtcod.console_put_char(con, x*2, y*2+1, tiles.get('wall_tile')+32, libtcod.BKGND_NONE)
                        libtcod.console_put_char(con, x*2+1, y*2+1, tiles.get('wall_tile')+33, libtcod.BKGND_NONE)

                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored:
                    libtcod.console_set_char_background(con, x * 2, y * 2, colors.get('dark'), libtcod.BKGND_SET)
                    libtcod.console_set_char_background(con, x * 2 + 1, y * 2, colors.get('dark'), libtcod.BKGND_SET)
                    libtcod.console_set_char_background(con, x * 2, y * 2 + 1, colors.get('dark'), libtcod.BKGND_SET)
                    libtcod.console_set_char_background(con, x * 2 + 1, y * 2 + 1, colors.get('dark'), libtcod.BKGND_SET)

                    if wall:
                        libtcod.console_put_char(con, x*2, y*2, tiles.get('wall_tile'), libtcod.BKGND_NONE)
                        libtcod.console_put_char(con, x*2+1, y*2, tiles.get('wall_tile')+1, libtcod.BKGND_NONE)
                        libtcod.console_put_char(con, x*2, y*2+1, tiles.get('wall_tile')+32, libtcod.BKGND_NONE)
                        libtcod.console_put_char(con, x*2+1, y*2+1, tiles.get('wall_tile')+33, libtcod.BKGND_NONE)
                else:
                    libtcod.console_set_char_background(con, x*2, y*2, colors.get('dark'), libtcod.BKGND_SET)
                    libtcod.console_set_char_background(con, x*2+1, y*2, colors.get('dark'), libtcod.BKGND_SET)
                    libtcod.console_set_char_background(con, x*2, y*2+1, colors.get('dark'), libtcod.BKGND_SET)
                    libtcod.console_set_char_background(con, x*2+1, y*2+1, colors.get('dark'), libtcod.BKGND_SET)

    # Draw all entities in the list

    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)

    for entity in entities_in_render_order:
        draw_entity(con, entity, fov_map,anim_frame)

    libtcod.console_blit(con, 0,0,map_width*2, map_height*2, 0, -cam_x, -cam_y)

    libtcod.console_set_default_background(panel, colors.get('light'))
    libtcod.console_clear(panel)

    # Print the game messages, one line at a time
    y = 1
    for message in message_log.messages:
        libtcod.console_set_default_foreground(panel, message.color)
        libtcod.console_print_ex(panel, message_log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text)
        y += 1

    render_bar(panel, 1, 1, bar_width, 'HP', player.fighter.hp, player.fighter.max_hp, colors.get('green'), colors.get('dark'), colors.get('light'))

    libtcod.console_set_default_background(panel, colors.get('dark'))
    libtcod.console_set_default_foreground(panel, libtcod.white)
    for x in range(0,screen_width):
        libtcod.console_put_char(panel, x, 0, tiles.get('gradient_tile'),libtcod.BKGND_SET)

    libtcod.console_set_default_foreground(panel, colors.get('dark'))
    libtcod.console_set_default_background(panel, colors.get('light'))
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_SET, libtcod.LEFT, get_names_under_mouse(cam_x,cam_y,mouse, entities, fov_map))

    libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)

    if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        if game_state == GameStates.SHOW_INVENTORY:
            inventory_title = 'Press the key next to an item to use it, or Esc to cancel.\n'
        else:
            inventory_title = 'Press the key next to an item to drop it, or Esc to cancel.\n'

        inventory_menu(con, inventory_title, player.inventory, 50, screen_width, screen_height)

def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)

def draw_entity(con, entity, fov_map,anim_frame):
    if libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
        libtcod.console_set_default_foreground(con, entity.color)
        if entity.render_order == RenderOrder.CORPSE:
            sprite = entity.char+256
        else:
            sprite = entity.char+(64*anim_frame)
        libtcod.console_put_char(con, entity.x * 2, entity.y * 2, sprite, libtcod.BKGND_NONE)
        libtcod.console_put_char(con, entity.x * 2+1, entity.y * 2, sprite+1, libtcod.BKGND_NONE)
        libtcod.console_put_char(con, entity.x * 2, entity.y * 2+1, sprite+32, libtcod.BKGND_NONE)
        libtcod.console_put_char(con, entity.x * 2+1, entity.y * 2+1, sprite+33, libtcod.BKGND_NONE)


def clear_entity(con, entity):
    # erase the character that represents this object
    libtcod.console_put_char(con, entity.x*2, entity.y*2, ' ', libtcod.BKGND_NONE)
    libtcod.console_put_char(con, entity.x*2+1, entity.y*2, ' ', libtcod.BKGND_NONE)
    libtcod.console_put_char(con, entity.x*2, entity.y*2+1, ' ', libtcod.BKGND_NONE)
    libtcod.console_put_char(con, entity.x*2+1, entity.y*2+1, ' ', libtcod.BKGND_NONE)