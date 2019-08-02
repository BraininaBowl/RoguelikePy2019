import libtcodpy as libtcod

tiles = {
    'wall_tile': 256,
    'player_tile': 259,
    'orc_tile': 262,
    'goblin_tile': 265,
    'troll_tile': 268,
    'scroll_tile': 271,
    'healingpotion_tile': 274,
    'sword_tile': 277,
    'shield_tile': 280,
    'dagger_tile': 283,
    'gradient_tile': 320,
    'stairsdown_tile': 352
}


colors = {
    'dark': libtcod.Color(53, 52, 42),
    'light': libtcod.Color(211, 210, 203),
    'green': libtcod.Color(77, 97, 60),
    'red': libtcod.Color(170, 61, 61)
}
