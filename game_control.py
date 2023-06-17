import pygame
from game.game_2d import Game2D
from game.game_3d import Game3D, X_AXIS, Y_AXIS, Z_AXIS
from game.move_data import *
from json import load as load_from_json
from collections.abc import Sequence


pygame.init()


CONTROLS_KEYS_NAMES: dict[str, str] = {
                action: key_names
            for action, key_names in load_from_json(open("keyboard_settings.json")).items()
}


CONTROLS_KEYS: dict[str, int] = {
    action: tuple(pygame.key.key_code(key_name) for key_name in key_names)
    for action, key_names in CONTROLS_KEYS_NAMES.items()
}


class GameControl:
    """
    Handles piece falling framerate and keyboard inputs.
    Contains Tetris Game2D/3D.
    """
    FIRST_DELAY = 15
    """
    The amount of frames the player must wait before moving a piece in the game,
    after the first frame of pressing the direction, in order to prevent the player
    from accidentally moving the piece more than once, when trying to move it
    a single block
    """
    SECOND_DELAY = 6
    """
    The amount of frames the player must wait before moving a piece in the game,
    in order to prevent the piece from going too fast
    """

    STARTING_DAS = {"previous_frame": False, "first_das": False, "charge": 0}
    def __init__(self, direction_keys: dict[str, Sequence[int]]):
        """
        'direction_keys' should be a dictionary of GAME directions:
        LEFT, RIGHT, FRONT, BACK
        and key codes:
        pygame.K_...
        """
        self.game = Game2D()

        self.frame_count = 0

        self.direction_keys: dict[str, Sequence[int]] = direction_keys
        self.das = {
            direction: GameControl.STARTING_DAS.copy()
            for direction in direction_keys.keys()
        }
        """
        "DAS" = "delayed auto shift".
        direction_key: charge setting (same as STARTING_DAS above)
        """
        self.game_can_continue = True

    @staticmethod
    def fall_rate(level):
        return int(49 / 1.1 ** level) + 1
    
    def direction_input_handler(self, keys):
        """
        Plays 'self.game' with direction keys found in 'keys'.

        Please call in 'self.input_handler' overrides.
        """

        for direction, direction_keys in self.direction_keys.items():

            if any(keys[key] for key in direction_keys):

                self.das[direction]["charge"] += 1

                if self.das[direction]["charge"] == GameControl.SECOND_DELAY and self.das[direction]["first_das"] or\
                        self.das[direction]["charge"] == GameControl.FIRST_DELAY:
                    self.game.try_move(direction)

                    self.das[direction]["charge"] = 0
                    self.das[direction]["first_das"] = True

                elif not self.das[direction]["previous_frame"]:
                    self.game.try_move(direction)

                    self.das[direction]["charge"] = 0
                    self.das[direction]["previous_frame"] = True

            else:
                if self.das[direction]["charge"] > 0:
                    self.das[direction]["charge"] -= 1
                self.das[direction]["first_das"] = False
                self.das[direction]["previous_frame"] = False

        # If we press a direction key, we charge the das bar.
        # The first frame the user presses the direction, the piece moves instantly.
        # The second time is called "first_das", where we wait GameControl.FIRST_DELAY frames to move the piece.
        # All the other times, we reach up to GameControl.SECOND_DELAY.
        # If user isn't moving, the charge goes down until it reaches 0, and "previous_frame" is set to False.

    def input_handler(self, key_down_keys: set[int]):
        """
        Checks for pygame key inputs and plays game accordingly.
        (abstract method to overriden in GameControl2D and GameControl3D)
        """
        raise NotImplementedError

    def play_game_step(self, key_down_keys: set[int]) -> bool:
        """
        Counts the amount of frames before playing next game step
        in 'self.frame_count'
        (because of the pieces' fall rate needing to be faster the
        higher the level),
        and plays the game's next step (using 'self.game.play')
        if the counter has hit the level's appropiate piece
        fall rate.
        (Look at 'fall_rate' for more info)

        Returns True if the game should keep going, and False
        if the player "topped-out", and the game is over.

        If the counter is still counting, this method's
        result is always True.
        """
        self.frame_count += 1
        self.input_handler(key_down_keys)

        if not self.game_can_continue:
            return False

        if self.frame_count == self.fall_rate(self.game.score_manager.level):
            self.game_can_continue = self.game.play()
            self.frame_count = 0

        return self.game_can_continue
    # Counting frames.


class GameControl2D(GameControl):
    def __init__(self):
        GameControl.__init__(
            self, 
            {
                LEFT: CONTROLS_KEYS["LEFT"],
                RIGHT: CONTROLS_KEYS["RIGHT"]
            }
        )
        self.game = Game2D()

    def input_handler(self, key_down_keys: set[int]):
        """Checks w, a, s, d, space bar, period and comma for in-game moves.
        Keeps track of left and right's das."""
        keys = pygame.key.get_pressed()

        GameControl.direction_input_handler(self, keys)

        if key_down_keys.intersection(CONTROLS_KEYS["rotate_cw_y"]):
            self.game.try_rotate()

        if key_down_keys.intersection(CONTROLS_KEYS["rotate_ccw_y"]):
            self.game.try_rotate(False)
        # ANY rotation key STARTING TO BE PRESSED this frame should rotate the piece,
        # EVEN if there's MORE THAN ONE rotation key being pressed at the same time.
        # there should only be ONE ROTATION!!!

        # Rotations should ONLY happen the frist frame the key is held,
        # to spamming the rotation every frame.

        if any(
            keys[key] for key in CONTROLS_KEYS["SOFT_DROP"] + CONTROLS_KEYS["DOWN"]
        ) and not self.game.landed():
            self.game.try_move(SOFT_DROP)

            if self.game.landed():
                self.frame_count = 0
        # If the piece that we soft-dropped landed,
        # the piece should remain there until the whole fram cycle finishes.
        # This makes it a lot easier to do T-spins and other things,
        # since the piece doesn't land immediatly after touching the ground.

        if key_down_keys.intersection(CONTROLS_KEYS["HARD_DROP"]):
            self.game.try_move(HARD_DROP)

            self.frame_count = self.fall_rate(self.game.score_manager.level)
            # If we hard dropped, the dropping cycle of the pieces will reset.


class GameControl3D(GameControl):
    def __init__(self):
        GameControl.__init__(
            self, 
            {
                LEFT: CONTROLS_KEYS["LEFT"],
                RIGHT: CONTROLS_KEYS["RIGHT"],
                FRONT: CONTROLS_KEYS["DOWN"],
                BACK: CONTROLS_KEYS["UP"]
            }
        )
        self.game = Game3D()

    def input_handler(self, key_down_keys: set[int]):
        """Checks w, a, s, d, space bar, period and comma for in-game moves.
        Keeps track of left and right's das."""
        keys = pygame.key.get_pressed()

        GameControl.direction_input_handler(self, keys)

        if any(keys[key] for key in CONTROLS_KEYS["SOFT_DROP"]):
            self.game.try_move(SOFT_DROP)

            if self.game.landed():
                self.frame_count = 0
        # If the piece that we soft-dropped landed,
        # the piece should remain there until the whole fram cycle finishes.
        # This makes it a lot easier to do T-spins and other things,
        # since the piece doesn't land immediatly after touching the ground.

        if key_down_keys.intersection(CONTROLS_KEYS["HARD_DROP"]):
            self.game.try_move(HARD_DROP)

            self.frame_count = self.fall_rate(self.game.score_manager.level)
            # If we hard dropped, the dropping cycle of the pieces will reset.
        
        for axis, axis_name in enumerate("xyz"):
            for clockwise in (True, False):
                ROTATION_NAME = f"rotate_{'cw' if clockwise else 'ccw'}_{axis_name}"
                if key_down_keys.intersection(CONTROLS_KEYS[ROTATION_NAME]):
                    self.game.try_rotate(axis, clockwise)
