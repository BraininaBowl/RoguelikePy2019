import tcod as libtcod
import math

from components.graphics import colors, tiles
from enum import Enum
from game_states import GameStates
from menus import character_screen, inventory_menu, level_up_menu

class RenderOrder(Enum):
    STAIRS = 1
    CORPSE = 2
    ITEM = 3
    ACTOR = 4

def distanceBetween(x1,y1,x2,y2):
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx ** 2 + dy ** 2)

def get_names_under_mouse(cam_x,cam_y,mouse, entities, fov_map):
    (x, y) = (mouse.cx+cam_x, mouse.cy+cam_y)
    names = [entity.name for entity in entities
             if (entity.x*3 == x or entity.x*3+1 == x or entity.x*3+2 == x) and (entity.y*2 == y or entity.y*2+1 == y) and libtcod.map_is_in_fov(fov_map, entity.x, entity.y)]
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
    libtcod.console_print_ex(panel, x+int(bar_width/2), y, libtcod.BKGND_NONE, libtcod.CENTER, '{0}: {1}/{2}'.format(name, value, maximum))

def render_all(con, panel, tooltip, messages_pane, inventory_pane, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, screen_height, map_width, map_height, panel_width, panel_height, panel_x, mouse, colors, cam_x, cam_y,anim_frame, game_state, targeting_item, log_scroll, log_height, inv_scroll, inv_height):

    libtcod.console_clear(0)

    if fov_recompute or game_state == GameStates.TARGETING:
        # Draw all the tiles in the game map
        libtcod.console_set_default_foreground(con, libtcod.white)
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight
                if visible:
                    if game_state == GameStates.TARGETING and distanceBetween(math.floor((mouse.cx + cam_x)/3), math.ceil((mouse.cy + cam_y)/2), x, y) <= targeting_item.item.targeting_radius:
                            backcolor = colors.get('red')
                    else:
                        backcolor = colors.get('light')
                    game_map.tiles[x][y].explored = True
                else:
                    backcolor = colors.get('dark')

                libtcod.console_set_char_background(con, x * 3, y * 2, backcolor, libtcod.BKGND_SET)
                libtcod.console_set_char_background(con, x * 3 + 1, y * 2, backcolor, libtcod.BKGND_SET)
                libtcod.console_set_char_background(con, x * 3 + 2, y * 2, backcolor, libtcod.BKGND_SET)
                libtcod.console_set_char_background(con, x * 3, y * 2 + 1, backcolor, libtcod.BKGND_SET)
                libtcod.console_set_char_background(con, x * 3 + 1, y * 2 + 1, backcolor, libtcod.BKGND_SET)
                libtcod.console_set_char_background(con, x * 3 + 2, y * 2 + 1, backcolor, libtcod.BKGND_SET)

                if (game_map.tiles[x][y].explored or visible) and wall:
                    libtcod.console_put_char(con, x*3, y*2, tiles.get('wall_tile'), libtcod.BKGND_NONE)
                    libtcod.console_put_char(con, x*3+1, y*2, tiles.get('wall_tile')+1, libtcod.BKGND_NONE)
                    libtcod.console_put_char(con, x*3+2, y*2, tiles.get('wall_tile')+2, libtcod.BKGND_NONE)
                    libtcod.console_put_char(con, x*3, y*2+1, tiles.get('wall_tile')+32, libtcod.BKGND_NONE)
                    libtcod.console_put_char(con, x*3+1, y*2+1, tiles.get('wall_tile')+33, libtcod.BKGND_NONE)
                    libtcod.console_put_char(con, x*3+2, y*2+1, tiles.get('wall_tile')+34, libtcod.BKGND_NONE)

    # Draw all entities in the list

    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)

    for entity in entities_in_render_order:
        draw_entity(con, entity, fov_map, anim_frame, game_map, game_state)

    libtcod.console_blit(con, 0,0,map_width*3, map_height*2, 0, -cam_x, -cam_y)



    libtcod.console_set_default_background(panel, colors.get('light'))
    libtcod.console_set_default_foreground(panel, colors.get('dark'))
    libtcod.console_clear(panel)

    # Print the game messages, one line at a time
    libtcod.console_print_ex(panel, int(panel_width / 2), 3, libtcod.BKGND_SET, libtcod.CENTER, "----- Messages -----")


    libtcod.console_set_default_background(messages_pane, colors.get('light'))
    libtcod.console_clear(messages_pane)
    y = 1
    for message in message_log.messages:
        libtcod.console_set_default_foreground(messages_pane, message.color)
        libtcod.console_print_ex(messages_pane, message_log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text)
        y += 1
#    if log_scroll > y - log_height:
#        log_scroll = y - log_height
    libtcod.console_blit(messages_pane, 0, y-log_height-log_scroll, panel_width-3, log_height, panel, 2, 4)

#    libtcod.console_set_default_background(panel, colors.get('dark'))
#    libtcod.console_set_default_foreground(panel, colors.get('light'))
#    libtcod.console_put_char(panel, panel_width-1, 5, " ", libtcod.BKGND_SET)
    libtcod.console_put_char(panel, panel_width-2, 4, tiles.get('up_tile'), libtcod.BKGND_SET)
#    libtcod.console_put_char(panel, panel_width-3, 5, " ", libtcod.BKGND_SET)
#    libtcod.console_put_char(panel, panel_width-1, 5+log_height, " ", libtcod.BKGND_SET)
    libtcod.console_put_char(panel, panel_width-2, 4+log_height, tiles.get('down_tile'), libtcod.BKGND_SET)
#    libtcod.console_put_char(panel, panel_width-3, 5+log_height, " ", libtcod.BKGND_SET)

    # Print the inventory items
#    libtcod.console_set_default_background(panel, colors.get('light'))
#    libtcod.console_set_default_foreground(panel, colors.get('dark'))
    libtcod.console_print_ex(panel, int(panel_width / 2), 5+log_height, libtcod.BKGND_SET, libtcod.CENTER, "----- Backpack -----")

    libtcod.console_set_default_background(inventory_pane, colors.get('light'))
    libtcod.console_set_default_foreground(inventory_pane, colors.get('dark'))
    libtcod.console_clear(inventory_pane)
    y = 1
    for item in player.inventory.items:
        if player.equipment.main_hand == item:
            libtcod.console_print_ex(inventory_pane, 0, y, libtcod.BKGND_NONE, libtcod.LEFT,'{0} ({1}) (on main hand)'.format(item.name, item.number))
        elif player.equipment.off_hand == item:
            libtcod.console_print_ex(inventory_pane, 0, y, libtcod.BKGND_NONE, libtcod.LEFT,'{0} ({1}) (on off hand)'.format(item.name, item.number))
        else:
            libtcod.console_print_ex(inventory_pane, 0, y, libtcod.BKGND_NONE, libtcod.LEFT,'{0} ({1})'.format(item.name, item.number))
        y += 1
#    if inv_scroll > y - inv_height:
#        inv_scroll = y - inv_height
    libtcod.console_blit(inventory_pane, 0, y-inv_height, panel_width-3, inv_height, panel, 2,6+log_height)

    render_bar(panel, 2, 1, panel_width-4, 'Health', player.fighter.hp, player.fighter.max_hp, colors.get('green'), colors.get('dark'), colors.get('light'))
    libtcod.console_set_default_foreground(panel, colors.get('dark'))
#    libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level: {0}'.format(game_map.dungeon_level))

#    libtcod.console_set_default_background(panel, colors.get('dark'))
#    libtcod.console_set_default_foreground(panel, libtcod.white)
#    for x in range(0,screen_width):
#        libtcod.console_put_char(panel, x, 0, tiles.get('gradient_tile'),libtcod.BKGND_SET)

    libtcod.console_set_default_foreground(panel, colors.get('dark'))
    libtcod.console_set_default_background(panel, colors.get('light'))

    libtcod.console_blit(panel, 0, 0, panel_width, panel_height, 0, panel_x,0)

    libtcod.console_set_default_foreground(tooltip, colors.get('light'))
    libtcod.console_set_default_background(tooltip, colors.get('dark'))
    tooltip_text = get_names_under_mouse(cam_x,cam_y,mouse, entities, fov_map)
    tooltip_len = len(tooltip_text)
    libtcod.console_set_default_background(tooltip, libtcod.black)
    libtcod.console_clear(tooltip)
    libtcod.console_set_default_foreground(tooltip, colors.get('light'))
    libtcod.console_set_default_background(tooltip, colors.get('dark'))
    libtcod.console_print_ex(tooltip, 0, 0, libtcod.BKGND_SET, libtcod.LEFT, tooltip_text)

    libtcod.console_set_key_color(tooltip,libtcod.black)
    libtcod.console_blit(tooltip, 0,0, tooltip_len, 1, 0, mouse.cx + 2, mouse.cy + 1)


    if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        if game_state == GameStates.SHOW_INVENTORY:
            inventory_title = 'Use or equip item.\n'
        else:
            inventory_title = 'Drop an item.\n'

        inventory_menu(con, inventory_title, player, 50, screen_width, screen_height)

    elif game_state == GameStates.LEVEL_UP:
        level_up_menu(con, 'Level up! Choose a stat to raise:', player, 40, screen_width, screen_height)

    elif game_state == GameStates.CHARACTER_SCREEN:
        character_screen(player, 30, 10, screen_width, screen_height)

def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)

def draw_entity(con, entity, fov_map, anim_frame, game_map, game_state):
    if libtcod.map_is_in_fov(fov_map, entity.x, entity.y) or (entity.stairs and game_map.tiles[entity.x][entity.y].explored):
        libtcod.console_set_default_foreground(con, entity.color)
        if entity.render_order == RenderOrder.CORPSE or (game_state == GameStates.PLAYER_DEAD and entity.name == "you"):
            sprite_main = entity.char+256
            sprite_off = sprite_main+1
        elif entity.stairs:
            sprite_main = entity.char
            sprite_off = sprite_main+1
        elif entity.equipment:
            if entity.equipment.main_hand:
                sprite_main = entity.char+(64*anim_frame) + entity.equipment.main_hand.sprite_main_shift
            else:
                sprite_main = entity.char+(64*anim_frame)
            if entity.equipment.off_hand:
                sprite_off = entity.char+(64*anim_frame) + 1 + entity.equipment.off_hand.sprite_off_shift
            else:
                sprite_off = entity.char+(64*anim_frame) + 1

        else:
            sprite_main = entity.char+(64*anim_frame)
            sprite_off = sprite_main + 1
        libtcod.console_put_char(con, entity.x * 3, entity.y * 2, sprite_main, libtcod.BKGND_NONE)
        libtcod.console_put_char(con, entity.x * 3+1, entity.y * 2, sprite_off, libtcod.BKGND_NONE)
        libtcod.console_put_char(con, entity.x * 3+2, entity.y * 2, sprite_off+1, libtcod.BKGND_NONE)
        libtcod.console_put_char(con, entity.x * 3, entity.y * 2+1, sprite_main+32, libtcod.BKGND_NONE)
        libtcod.console_put_char(con, entity.x * 3+1, entity.y * 2+1, sprite_off+32, libtcod.BKGND_NONE)
        libtcod.console_put_char(con, entity.x * 3+2, entity.y * 2+1, sprite_off+33, libtcod.BKGND_NONE)

def clear_entity(con, entity):
    # erase the character that represents this object
    libtcod.console_put_char(con, entity.x*3, entity.y*2, ' ', libtcod.BKGND_NONE)
    libtcod.console_put_char(con, entity.x*3+1, entity.y*2, ' ', libtcod.BKGND_NONE)
    libtcod.console_put_char(con, entity.x*3+2, entity.y*2, ' ', libtcod.BKGND_NONE)
    libtcod.console_put_char(con, entity.x*3, entity.y*2+1, ' ', libtcod.BKGND_NONE)
    libtcod.console_put_char(con, entity.x*3+1, entity.y*2+1, ' ', libtcod.BKGND_NONE)
    libtcod.console_put_char(con, entity.x*3+2, entity.y*2+1, ' ', libtcod.BKGND_NONE)