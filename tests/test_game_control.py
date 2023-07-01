import game_control
from game.game_2d import I, J, L, O, S, T, Z, Piece2D, COLUMNS
from game.game_3d import PIECES_3D, Piece3D, FLOOR_WIDTH
from itertools import count
import unittest


PIECES_2D = (I, J, L, O, S, T, Z)


class TestGameControl(unittest.TestCase):
    def test_das(self):
        """
        DAS, or delayed auto shift, is responsible for moving the pieces at a certain speed,
        without having to lift the finger.

        When the player first presses a direction key,
        the key should move one block in that direction immediately,
        then should wait for 'GameControl.FIRST_DELAY' frames before moving another block.
        After this point is reached, if the player continues to hold the direction key,
        the piece should move in intervals of 'GameControl.SECOND_DELAY' frames.

        If the first frame move fails, the frame counter should continue increasing,
        until it reaches 'GameControl.FIRST_DELAY' + 1, or until the piece finally succeeded moving,
        then should proceed normally, like above.

        This is to prevent the piece from going too fast,
        from the player accidentally moving the piece more than one block over
        when they only intended to move if one,
        and from missing a frame-perfect tuck.

        Yes, this also means the player could spam the key
        to go even faster, if they really tried, as long as
        the 'GameControl.SECOND_DELAY' is above 2.

        In order to test that GameControl works this way,
        this method EMULATES holding LEFT in the game,
        then checks that the piece moved at frame #0,
        frame #GameControl.FIRST_DEALY and frame #GameControl.SECOND_DELAY,
        IN A WAY THAT PREVENTS THE PIECE FROM HITTING THE WALL, AND FALSIFYING THE TEST.
        """
        class KeysLeftTest:
            """
            Impersonates 'pygame.key.get_pressed()',
            AS IF the LEFT keys were being pressed.
            """
            def __getitem__(self, key: int):
                return key in game_control.controls_keys["LEFT"]


        # WE DO NOT NEED TO TEST IT IN 3D,
        # SINCE THE 2D's 'direction_input_handler' METHOD
        # IS INHERITED FROM 'GameControl',
        # AS IS THE 3D's
        for piece in PIECES_2D:
            gc2D = game_control.GameControl2D()
            gc2D.game.piece = Piece2D(piece)

            for frame in range(22):
                FRAME_SUCCESSFUL: bool = gc2D.direction_input_handler(KeysLeftTest())

                if frame == 0 \
                        or frame == game_control.GameControl.FIRST_DELAY \
                    or frame == game_control.GameControl.FIRST_DELAY + game_control.GameControl.SECOND_DELAY:
                        self.assertTrue(FRAME_SUCCESSFUL, msg=str(frame))
                else:
                    self.assertFalse(FRAME_SUCCESSFUL, msg=str(frame))

