"""
All of the game's sounds,
the audio in this directory,
as 'pygame.mixer.Sound' objects.

Also contains 'SXF_CHANNEL', a 'pygame.mixer.Channel'
to play the SFX's in.
"""
from pygame import mixer

SCROLLING_OVER_MENU_OPTION = \
    mixer.Sound("sound/scrolling_over_menu_option.mp3")
SUBMITED_IN_MENU = mixer.Sound("sound/submited_in_menu.mp3")
CLEARED_BLOCKS = mixer.Sound("sound/blocks_cleared.mp3")
GAME_OVER = mixer.Sound("sound/game_over.mp3")
ROTATING_PIECE = mixer.Sound("sound/rotating_piece.mp3")
HARD_DROPPING_PIECE = mixer.Sound("sound/hard_dropping_piece.mp3")
CHANGED_CONTROL_KEY = mixer.Sound("sound/changed_control_key.wav")
SFX_CHANNEL = mixer.Channel(0)
"""
pygame sound channel to play all of the SFX's in this file
"""
