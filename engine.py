import libtcodpy as libtcod

from components.fighter import Fighter
from death_functions import kill_monster, kill_player
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from render_functions import clear_all, render_all


def load_customfont():
    # The index of the first custom tile in the file
    a = 256

    # The "y" is the row index, here we load the sixth row in the font file. Increase the "6" to load any new rows from the file
    for y in range(5, 6):
        libtcod.console_map_ascii_codes_to_font(a, 32, 0, y)
        a += 32

def main():
    screen_width = 60
    screen_height = 40

    # Size of the map
    map_width = 60
    map_height = 40

    #camera position
    cam_x = screen_width/2
    cam_y = screen_height/2

    # Some variables for the rooms in the map
    room_max_size = 10
    room_min_size = 6
    max_rooms = 20

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    max_monsters_per_room = 3

    wall_tile = 256
    floor_tile = 257
    player_tile = 258
    orc_tile = 259
    troll_tile = 260
    scroll_tile = 261
    healingpotion_tile = 262
    sword_tile = 263
    shield_tile = 264
    stairsdown_tile = 265
    dagger_tile = 266

    colors = {
        'dark': libtcod.Color(53, 52, 42),
        'light': libtcod.Color(211, 210, 203),
        'green': libtcod.Color(77, 97, 60)
    }

    fighter_component = Fighter(hp=30, defense=2, power=5)
    player = Entity(0, 0, player_tile, libtcod.white, 'Player', blocks=True, fighter=fighter_component)
    entities = [player]

    libtcod.console_set_custom_font('sprite-font.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD, 32, 10)

    libtcod.console_init_root(screen_width, screen_height, 'A bird underground', False)

    load_customfont()

    con = libtcod.console_new(screen_width, screen_height)

    game_map = GameMap(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities,
                      max_monsters_per_room)

    cam_x = screen_width / 2 - player.x
    cam_y = screen_height / 2 - player.y

    fov_recompute = True

    fov_map = initialize_fov(game_map)

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    game_state = GameStates.PLAYERS_TURN

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

        render_all(con, entities, player, game_map, fov_map, fov_recompute, screen_width, screen_height, colors, cam_x, cam_y)

        fov_recompute = False

        libtcod.console_flush()

        clear_all(con, entities)

        action = handle_keys(key)

        move = action.get('move')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

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
                    cam_x = screen_width/2 - player.x
                    cam_y = screen_height/2 - player.y
                    fov_recompute = True

            else:
                print('You stupidly walk into the wall. Ouch.')
            game_state = GameStates.ENEMY_TURN

        if exit:
            return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')

            if message:
                print(message)

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                print(message)

        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')

                        if message:
                            print(message)

                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            print(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break

            else:
                game_state = GameStates.PLAYERS_TURN


if __name__ == '__main__':
    main()