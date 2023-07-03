import pygame
from game.game_2d import Game2D
from game.game_3d import Game3D, X_AXIS, Y_AXIS, Z_AXIS
from game.move_data import *
from json import load as load_from_json
from collections.abc import Sequence
from dataclasses import dataclass


pygame.init()

CONTROL_KEYS_FILE = "keyboard_settings.json"

controls_keys: dict[str, list[int]] = {
                action: [pygame.key.key_code(key_name) for key_name in key_names]
            for action, key_names in load_from_json(open(CONTROL_KEYS_FILE)).items()
}
"""
Dict of modes and their actions,
together with the list of key CODES (aka pygame.K_{key_name})
that perform that action.

SHOULD BE EDITED IN 'main.py', AS AN INTERNAL GLOBAL VARIABLE.
"""


@dataclass
class SuccessfulActions:
    """
    The in-game actions that were performed,
    AND SUCCEEDED.

    For example:
    Game2D.try_move
    Game3D.try_rotate
    """
    moving_in_das_direction: bool
    hard_dropping: bool
    moving_one_block_down: bool
    rotating: bool


@dataclass
class DASSettings:
    first_move_pending: bool = False
    charge: int = 0

    def copy(self):
        return DASSettings(self.first_move_pending, self.charge)


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

    def __init__(self, directions: Sequence[str]):
        """
        'directions' SHOULD be an iterale of IN-GAME DIRECTIONS:
        LEFT, RIGHT, FRONT, BACK

        THIS METHOD DOES NOT VALIDATE THEM,
        THE GameControl2D and GameControl3D CHILDREN OF THIS CLASS
        MUST.
        """
        self.game = Game2D()

        self.frame_count = 0

        self.das = {
            direction: DASSettings()
            for direction in directions
        }
        """
        "DAS" = "delayed auto shift".
        direction_key: charge setting (same as STARTING_DAS above)
        """
        self.game_can_continue = True

    @staticmethod
    def fall_rate(level):
        return int(49 / 1.1 ** level) + 1
    
    def direction_input_handler(self, pressed_directions: set[str]) -> bool:
        """
        Calls 'self.game.try_move' with the directions corresponding
        to the pressed direction keys,

        ASSUMING THAT:
        - 'pressed_directions' has all of the VALID DIRECTIONS
        (LEFT, RIGHT BACK, FRONT) that the player is currently
        holding down in their keyboard.

        BUT only if the player has already been holding those direction key(s) down
        for a certain amount of frames. The first time the player holds
        a direction down on a cold start, the first frame, its
        "self.game.try_move(<direction>)" will be called.
        then, this object will count up to 'GameControl.FIRST_DELAY'
        before the piece actually gets moved again.

        This is to prevent the player from accidentally moving the piece
        more than one block, when the player is quickly tapping the direction key(s).

        After that press, the player will have to keep waiting
        'GameControl.SECOND_DELAY' frames before the next direction press.
        This is to make the piece move at a reasonable speed, unlike the framerate,
        which may be 60FPS, causing the piece to fly into the wall
        at the slightest tap.

        This should work well, IF THE FIRST DELAY IS BIGGER THAN THE SECOND DELAY,
        AND IF THEIR SPEEDS ARE REASONABLE.

        Plays 'self.game' with 'directions',
        by calling 'self.game.try_move(<direction>)',
        ASSUMING THE PLAYER IS HOLDING DOWN THOSE DIRECTIONS IN THEIR KEYBOARD,
        IF THE DIRECTION IS READY TO BE PRESSED, BASED ON THE AMOUNT OF FRAMES
        IT'S BEEN HELD DOWN, LIKE MENTIONED JUST ABOVE HERE.

        After all of this,
        this method returns True if ANY of these directions tried in
        'self.game.try_move(<direction>)',
        and False if NONE of the moves were made.

        Please call in 'self.input_handler' overrides.
        """

        moved: bool = False

        for direction in self.das.keys():
            # dictionary keys, 'direction' SHOULD be 'str'.

            assert isinstance(direction, str)

            direction_moved: bool = False

            if direction in pressed_directions:

                if self.das[direction].charge == 0:
                    direction_moved = self.game.try_move(direction)
                    self.das[direction].first_move_pending = not direction_moved

                    self.das[direction].charge += 1
                elif self.das[direction].charge == GameControl.FIRST_DELAY:
                    direction_moved = self.game.try_move(direction)
                    self.das[direction].first_move_pending = False

                    if direction_moved:
                        self.das[direction].charge += 1
                
                elif self.das[direction].charge == GameControl.FIRST_DELAY + GameControl.SECOND_DELAY:
                    direction_moved = self.game.try_move(direction)
                    self.das[direction].first_move_pending = False

                    self.das[direction].charge = GameControl.FIRST_DELAY

                    if direction_moved:
                        self.das[direction].charge += 1

                elif self.das[direction].first_move_pending:
                    direction_moved = self.game.try_move(direction)
                    self.das[direction].first_move_pending = not direction_moved

                    if 0 < GameControl.FIRST_DELAY - self.das[direction].charge <= GameControl.SECOND_DELAY:
                        self.das[direction].charge = GameControl.FIRST_DELAY + 1
                        self.das[direction].first_move_pending = False
                else:
                    self.das[direction].charge += 1
            else:
                self.das[direction].charge = 0
                self.das[direction].first_move_pending = False

            if direction_moved:
                moved = True

        # print(self.das, moved)

        return moved

    def input_handler(self, key_down_keys: set[int]) -> SuccessfulActions:
        """
        Checks for in-game moves' keys in 'key_down_keys',
        ASSUMING that 'key_down_keys' CONTAINS THE KEYS
        JUST STARTED BEING PRESSED,

        and uses 'pygame.key.get_pressed' to get ALL
        of the keys CURRENTLY being pressed REGARDLESS
        of the previous frame,

        to play their corresponding in-game actions as stored in
        'controls_keys'.

        Returns the different types of actions that were successful
        (like rotating, moving, soft-dropping and hard-dropping)
        """
        raise NotImplementedError

    def play_game_step(self, key_down_keys: set[int]) -> tuple[SuccessfulActions, bool]:
        """
        Counts the amount of frames before playing next game step
        in 'self.frame_count'
        (because of the pieces' fall rate needing to be faster the
        higher the level),
        and plays the game's next step (using 'self.game.play')
        if the counter has hit the level's appropiate piece
        fall rate.
        (Look at 'fall_rate' for more info)

        Returns the successfull actions performed with keyboard inputs,
        and weather or not the game can keep going.

        If the counter is still counting, this method's
        result is always True.
        """
        self.frame_count += 1
        
        succeessful_actions: SuccessfulActions = self.input_handler(key_down_keys)

        if not self.game_can_continue:
            return succeessful_actions, False

        if self.frame_count == self.fall_rate(self.game.score_manager.level):
            self.game_can_continue = self.game.play()
            self.frame_count = 0

        return succeessful_actions, self.game_can_continue
    # Counting frames.


class GameControl2D(GameControl):
    def __init__(self):
        GameControl.__init__(self, (LEFT, RIGHT))
        self.game = Game2D()

    def input_handler(self, key_down_keys: set[int]) -> SuccessfulActions:
        """
        Checks for in-game moves' keys in 'key_down_keys',
        ASSUMING that 'key_down_keys' CONTAINS THE KEYS
        JUST STARTED BEING PRESSED,

        and uses 'pygame.key.get_pressed' to get ALL
        of the keys CURRENTLY being pressed REGARDLESS
        of the previous frame,

        to play their corresponding in-game actions as stored in
        'controls_keys'.

        Returns the different types of actions that were successful
        (like rotating, moving, soft-dropping and hard-dropping)
        """
        keys = pygame.key.get_pressed()

        result = SuccessfulActions(False, False, False, False)

        pressed_directions: set[str] = set()

        if any(keys[key] for key in controls_keys["LEFT"]):
            pressed_directions.add(LEFT)
        if any(keys[key] for key in controls_keys["RIGHT"]):
            pressed_directions.add(RIGHT)
        
        if LEFT in pressed_directions and RIGHT in pressed_directions:
            pressed_directions = set()

        result.moving_in_das_direction = GameControl.direction_input_handler(self, pressed_directions)

        if pressed_directions == set():
            assert result.moving_in_das_direction == False

        if key_down_keys.intersection(controls_keys["rotate_cw_y"]):
            result.rotating = self.game.try_rotate()

        if key_down_keys.intersection(controls_keys["rotate_ccw_y"]):
            result.rotating = self.game.try_rotate(False)
        # ANY rotation key STARTING TO BE PRESSED this frame should rotate the piece,
        # EVEN if there's MORE THAN ONE rotation key being pressed at the same time.
        # there should only be ONE ROTATION!!!

        # Rotations should ONLY happen the frist frame the key is held,
        # to spamming the rotation every frame.

        if any(
            keys[key] for key in controls_keys["SOFT_DROP"] + controls_keys["DOWN"]
        ) and not self.game.landed():
            result.moving_one_block_down = self.game.try_move(SOFT_DROP)

            if self.game.landed():
                self.frame_count = 0
        # If the piece that we soft-dropped landed,
        # the piece should remain there until the whole fram cycle finishes.
        # This makes it a lot easier to do T-spins and other things,
        # since the piece doesn't land immediatly after touching the ground.

        if key_down_keys.intersection(controls_keys["HARD_DROP"]):
            result.hard_dropping = self.game.try_move(HARD_DROP)

            self.frame_count = self.fall_rate(self.game.score_manager.level)
            # If we hard dropped, the dropping cycle of the pieces will reset.
        
        return result


class GameControl3D(GameControl):
    def __init__(self):
        GameControl.__init__(
            self, 
            {
                LEFT: controls_keys["LEFT"],
                RIGHT: controls_keys["RIGHT"],
                FRONT: controls_keys["DOWN"],
                BACK: controls_keys["UP"]
            }
        )
        self.game = Game3D()

    def input_handler(self, key_down_keys: set[int]):
        """
        Checks for in-game moves' keys in 'key_down_keys',
        ASSUMING that 'key_down_keys' CONTAINS THE KEYS
        JUST STARTED BEING PRESSED,

        and uses 'pygame.key.get_pressed' to get ALL
        of the keys CURRENTLY being pressed REGARDLESS
        of the previous frame,

        to play their corresponding in-game actions as stored in
        'controls_keys'.

        Returns the different types of actions that were successful
        (like rotating, moving, soft-dropping and hard-dropping)
        """
        keys = pygame.key.get_pressed()
        result = SuccessfulActions(False, False, False, False)

        result.moving_in_das_direction = GameControl.direction_input_handler(self, keys)

        if any(keys[key] for key in controls_keys["SOFT_DROP"]):
            result.moving_one_block_down = self.game.try_move(SOFT_DROP)

            if self.game.landed():
                self.frame_count = 0
        # If the piece that we soft-dropped landed,
        # the piece should remain there until the whole fram cycle finishes.
        # This makes it a lot easier to do T-spins and other things,
        # since the piece doesn't land immediatly after touching the ground.

        if key_down_keys.intersection(controls_keys["HARD_DROP"]):
            result.hard_dropping = self.game.try_move(HARD_DROP)

            self.frame_count = self.fall_rate(self.game.score_manager.level)
            # If we hard dropped, the dropping cycle of the pieces will reset.
        
        for axis, axis_name in enumerate("xyz"):
            for clockwise in (True, False):
                ROTATION_NAME = f"rotate_{'cw' if clockwise else 'ccw'}_{axis_name}"
                if key_down_keys.intersection(controls_keys[ROTATION_NAME]):

                    ROTATION_SUCCESS: bool = self.game.try_rotate(axis, clockwise)

                    if ROTATION_SUCCESS:
                        result.rotating = True
                    # all we need is one rotation to succeed to set
                    # result.rotating to True.

        return result
