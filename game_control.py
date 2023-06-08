import pygame
from game.game_2d import Game2D
from game.game_3d import Game3D, X_AXIS, Y_AXIS, Z_AXIS
from game.move_data import *


class GameControl:
    STARTING_DAS = {"previous_frame": False, "first_das": False, "charge": 0}
    def __init__(self):
        self.game = Game2D()

        self.frame_count = 0
        self.das = {}
        # "DAS" = "delayed auto shift".
        # direction_key: charge setting (same as STARTING_DAS above)

    @staticmethod
    def fall_rate(level):
        return int(49 / 1.1 ** level) + 1

    def input_handler(self, key_down_keys: set[int]):
        """
        Checks for pygame key inputs and plays game accordingly.
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

        game_can_continue = True

        if self.frame_count == self.fall_rate(self.game.score_manager.level):
            game_can_continue = self.game.play()
            self.frame_count = 0

        return game_can_continue
    # Counting frames.


class GameControl2D(GameControl):
    def __init__(self):
        GameControl.__init__(self)

        self.game = Game2D()
        self.das = {
            LEFT: GameControl.STARTING_DAS.copy(),
            RIGHT: GameControl.STARTING_DAS.copy()
        }

    def input_handler(self, key_down_keys: set[int]):
        """Checks w, a, s, d, space bar, period and comma for in-game moves.
        Keeps track of left and right's das."""
        keys = pygame.key.get_pressed()

        DIRECTION_KEYS = {pygame.K_a: LEFT, pygame.K_d: RIGHT}

        for direction_key, direction in DIRECTION_KEYS.items():
            if keys[direction_key]:
                self.das[direction]["charge"] += 1

                if self.das[direction]["charge"] == 6 and self.das[direction]["first_das"] or\
                        self.das[direction]["charge"] == 15:
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

        # If we press left or right, we charge the das bar.
        # The first frame the user presses the direction, the piece moves instantly.
        # The second time is called "first_das", where we wait 15 frames to move the piece.
        # All the other times, we reach up to 6.
        # If user isn't moving, the charge goes down until it reaches 0, and "previous_frame" is set to False.

        if pygame.K_o in key_down_keys:
            self.game.try_rotate()

        if pygame.K_u in key_down_keys:
            self.game.try_rotate(False)
        # Rotations shouldn't happen every frame.

        if (keys[pygame.K_s] or keys[pygame.K_LSHIFT]) and not self.game.landed():
            self.game.try_move(SOFT_DROP)

            if self.game.landed():
                self.frame_count = 0
        # If the piece that we soft-dropped landed,
        # the piece should remain there until the whole fram cycle finishes.
        # This makes it a lot easier to do T-spins and other things,
        # since the piece doesn't land immediatly after touching the ground.

        if pygame.K_SPACE in key_down_keys:
            self.game.try_move(HARD_DROP)

            self.frame_count = self.fall_rate(self.game.score_manager.level)
            # If we hard dropped, the dropping cycle of the pieces will reset.


class GameControl3D(GameControl):
    def __init__(self):
        GameControl.__init__(self)

        self.game = Game3D()

        self.frame_count = 0

        self.das_bar = [15, 6]
        self.das = {
            LEFT: GameControl.STARTING_DAS.copy(),
            RIGHT: GameControl.STARTING_DAS.copy(),
            BACK: GameControl.STARTING_DAS.copy(),
            FRONT: GameControl.STARTING_DAS.copy()
        }
        # "DAS" = "delayed auto shift".

    def input_handler(self, key_down_keys: set[int]):
        """Checks w, a, s, d, space bar, period and comma for in-game moves.
        Keeps track of left and right's das."""
        keys = pygame.key.get_pressed()

        DIRECTION_KEYS = {pygame.K_a: LEFT, pygame.K_d: RIGHT, pygame.K_w: BACK, pygame.K_s: FRONT}

        for direction_key, direction in DIRECTION_KEYS.items():
            if keys[direction_key]:
                self.das[direction]["charge"] += 1

                if self.das[direction]["charge"] == 6 and self.das[direction]["first_das"] or\
                        self.das[direction]["charge"] == 15:
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

        # If we press left or right, we charge the das bar.
        # The first frame the user presses the direction, the piece moves instantly.
        # The second time is called "first_das", where we wait 15 frames to move the piece.
        # All the other times, we reach up to 6.
        # If user isn't moving, the charge goes down until it reaches 0, and "previous_frame" is set to False.

        if keys[pygame.K_LSHIFT] and not self.game.landed():
            self.game.try_move(SOFT_DROP)

            if self.game.landed():
                self.frame_count = 0
        # If the piece that we soft-dropped landed,
        # the piece should remain there until the whole fram cycle finishes.
        # This makes it a lot easier to do T-spins and other things,
        # since the piece doesn't land immediatly after touching the ground.

        if pygame.K_SPACE in key_down_keys:
            self.game.try_move(HARD_DROP)

            self.frame_count = self.fall_rate(self.game.score_manager.level)
            # If we hard dropped, the dropping cycle of the pieces will reset.

        rotations = {
            pygame.K_u: (Y_AXIS, False),
            pygame.K_o: (Y_AXIS, True),
            pygame.K_i: (X_AXIS, True),
            pygame.K_k: (X_AXIS, False),
            pygame.K_j: (Z_AXIS, True),
            pygame.K_l: (Z_AXIS, False)
        }
        # U: rotate around the y axis counter-clockwise
        # O: rotate around the y axis clockwise
        # I: rotate around the x axis clockwise
        # K: rotate around the x axis counter-clockwise
        # J: rotate around the z axis counter-clockwise
        # L: rotate around the z axis clockwise

        # (Imagine flicking the piece from it's sides,
        # like in 2D)

        # ROTATE WITH KEYS
        for rotation_key, (axis, clockwise) in rotations.items():
            if rotation_key in key_down_keys:
                self.game.try_rotate(axis, clockwise)
