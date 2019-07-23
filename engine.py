import tcod as libtcod

from components.graphics import colors
from death_functions import kill_monster, kill_player
from entity import get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_messages import Message
from game_states import GameStates
from input_handlers import handle_keys, handle_mouse, handle_main_menu
from loader_functions.initialize_new_game import get_constants, get_game_variables
from loader_functions.data_loaders import load_game, save_game
from menus import main_menu, message_box
from render_functions import clear_all, render_all

def load_customfont():
    # The index of the first custom tile in the file
    a = 256

    # The "y" is the row index, here we load the sixth row in the font file. Increase the "6" to load any new rows from the file
    for y in range(5, 18):
        libtcod.console_map_ascii_codes_to_font(a, 32, 0, y)
        a += 32

def animation (anim_frame, anim_time):
    if libtcod.sys_elapsed_milli() - anim_time > 200:
        anim_time = libtcod.sys_elapsed_milli()
        if anim_frame < 3:
            anim_frame += 1
        else:
            anim_frame = 0
    return anim_frame, anim_time


def update_cam(player, constants):
    cam_x = int(player.x * 2 - constants['screen_width'] / 2)
    cam_y = int(player.y * 2 - (constants['screen_height'] - constants['panel_height']) / 2)

    return cam_x,cam_y

def play_game(player, entities, game_map, message_log, game_state, con, panel, constants, cam_x, cam_y, anim_frame, anim_time):

    fov_recompute = True
    fov_map = initialize_fov(game_map)

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    game_state = GameStates.PLAYERS_TURN
    previous_game_state = game_state

    targeting_item = None

    while not libtcod.console_is_window_closed():
        anim_frame, anim_time = animation(anim_frame,anim_time)

        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, constants['fov_radius'], constants['fov_light_walls'], constants['fov_algorithm'])

        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, constants['screen_width'], constants['screen_height'], constants['map_width'], constants['map_height'], constants['bar_width'], constants['panel_height'], constants['panel_y'], mouse, colors, cam_x, cam_y, anim_frame, game_state, targeting_item)

        fov_recompute = False

        libtcod.console_flush()

        clear_all(con, entities)

        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse, cam_x, cam_y)

        move = action.get('move')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        inventory_index = action.get('inventory_index')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        player_turn_results = []

        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy

            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                if target:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)
                    cam_x, cam_y = update_cam(player, constants)
                    fov_recompute = True

            else:
                message_log.add_message(Message('You stupidly walk into the wall. Ouch.'))
            game_state = GameStates.ENEMY_TURN

        elif pickup and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)
                    break
            else:
                message_log.add_message(Message('There is nothing here to pick up.'))

        if show_inventory:
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        if drop_inventory:
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(
                player.inventory.items):
            item = player.inventory.items[inventory_index]

            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inventory.use(targeting_item, entities=entities, fov_map=fov_map,
                                                        target_x=target_x, target_y=target_y)
                player_turn_results.extend(item_use_results)
                fov_recompute = True
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})
                fov_recompute = True

        if exit:
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            else:
                save_game(player, entities, game_map, message_log, game_state)
                return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')

            if message:
                message_log.add_message(message)

            if targeting_cancelled:
                game_state = previous_game_state
                message_log.add_message(Message('Targeting cancelled'))
                fov_recompute = True

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

            if item_added:
                entities.remove(item_added)

                game_state = GameStates.ENEMY_TURN

            if item_consumed:
                game_state = GameStates.ENEMY_TURN

            if targeting:
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING

                targeting_item = targeting

                message_log.add_message(targeting_item.item.targeting_message)

            if item_dropped:
                entities.append(item_dropped)

                game_state = GameStates.ENEMY_TURN

        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')

                        if message:
                            message_log.add_message(message)

                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break

            else:
                game_state = GameStates.PLAYERS_TURN



def main():
    constants = get_constants()

    libtcod.sys_set_fps(30)

    # Animate
    anim_time = libtcod.sys_elapsed_milli()
    anim_frame = 0

    libtcod.console_set_custom_font('sprite-font.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD, 32, 22)
    libtcod.console_init_root(constants['screen_width'], constants['screen_height'], constants['window_title'], False)
    libtcod.console_set_default_background(0, colors.get('dark'))

    load_customfont()

    con = libtcod.console_new(constants['map_width']*2, constants['map_height']*2)
    panel = libtcod.console_new(constants['screen_width'], constants['panel_height'])

    player = None
    entities = []
    game_map = None
    message_log = None
    game_state = None

    show_main_menu = True
    show_load_error_message = False

    main_menu_background_image_0 = libtcod.image_load('menu_background_0.png')
    main_menu_background_image_1 = libtcod.image_load('menu_background_1.png')
    main_menu_background_image_2 = libtcod.image_load('menu_background_2.png')
    main_menu_background_image_3 = libtcod.image_load('menu_background_3.png')

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    while not libtcod.console_is_window_closed():

        anim_frame, anim_time = animation(anim_frame, anim_time)

        if anim_frame == 0:
            main_menu_background_image = main_menu_background_image_0
        elif anim_frame == 1:
            main_menu_background_image = main_menu_background_image_1
        elif anim_frame == 2:
            main_menu_background_image = main_menu_background_image_2
        else:
            main_menu_background_image = main_menu_background_image_3

        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if show_main_menu:
            main_menu(con, main_menu_background_image, constants['screen_width'],
                      constants['screen_height'], constants['window_title'])

            if show_load_error_message:
                message_box(con, 'No save game to load', 50, constants['screen_width'], constants['screen_height'])

            libtcod.console_flush()

            action = handle_main_menu(key)

            new_game = action.get('new_game')
            load_saved_game = action.get('load_game')
            exit_game = action.get('exit')

            if show_load_error_message and (new_game or load_saved_game or exit_game):
                show_load_error_message = False
            elif new_game:
                player, entities, game_map, message_log, game_state = get_game_variables(constants)
                game_state = GameStates.PLAYERS_TURN

                show_main_menu = False
            elif load_saved_game:
                try:
                    player, entities, game_map, message_log, game_state = load_game()
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error_message = True
            elif exit_game:
                break

        else:
            libtcod.console_clear(con)
            cam_x, cam_y = update_cam(player, constants)
            play_game(player, entities, game_map, message_log, game_state, con, panel, constants, cam_x, cam_y, anim_frame, anim_time)

            show_main_menu = True


if __name__ == '__main__':
    main()

                 