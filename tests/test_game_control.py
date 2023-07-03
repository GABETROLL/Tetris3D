import game_control
import pygame
from json import load as load_from_json
from game.move_data import *
from game.game_2d import I, J, L, O, S, T, Z, Piece2D
import unittest


PIECES_2D = (I, J, L, O, S, T, Z)


class TestCustomControls(unittest.TestCase):
    """
    Tests that the controls loaded from the custom controls JSON file
    ACTUALLY match it.
    """

    # (amlost?) REDUNDANT
    def test_loaded_controls(self):
        CONTROLS_KEYS_NAMES = load_from_json(open(game_control.CONTROL_KEYS_FILE))

        self.assertTrue(isinstance(CONTROLS_KEYS_NAMES, dict))

        EXPECTED_CONTROLS_KEYS = {
            action: [pygame.key.key_code(key_name) for key_name in key_names]
            for action, key_names in CONTROLS_KEYS_NAMES.items()
        }

        self.assertEqual(EXPECTED_CONTROLS_KEYS, game_control.controls_keys)
        


class TestSoftDrop(unittest.TestCase):
    def test_main(self):
        """
        Tests that soft-dropping moves down
        one block per frame.
        """
        instance_2D = game_control.GameControl2D()

        for frame in range(10):
            EXPECTED_POS = instance_2D.game.piece.pos
            instance_2D.input_handler(set(SOFT_DROP, ))
            EXPECTED_POS[1] += 1
            self.assertTrue(instance_2D.game.piece.pos == EXPECTED_POS)


class TestDirectionInputs(unittest.TestCase):
    def test_only_left_simplest(self):
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

        # WE DO NOT NEED TO TEST IT IN 3D,
        # SINCE THE 2D's 'direction_input_handler' METHOD
        # IS INHERITED FROM 'GameControl',
        # AS IS THE 3D's
        for piece in PIECES_2D:
            gc2D = game_control.GameControl2D()
            gc2D.game.piece = Piece2D(piece)

            for frame in range(22):
                FRAME_SUCCESSFUL: bool = gc2D.direction_input_handler((LEFT, ))

                if frame == 0 \
                        or frame == game_control.GameControl.FIRST_DELAY \
                    or frame == game_control.GameControl.FIRST_DELAY + game_control.GameControl.SECOND_DELAY:
                        self.assertTrue(FRAME_SUCCESSFUL, msg=f"{frame=} {gc2D.game.piece=} {gc2D.game.board=}")
                else:
                    self.assertFalse(FRAME_SUCCESSFUL, msg=str(frame))

    def test_buffered_tuck_before_second_delay(self):
        """
        THIS TEST DEPENDS ON 'TestSoftDrop' TO SUCCEED TO HAVE ITS RESULTS
        BE VALID.

        However, if the player starts trying to move a piece
        into a wall, where the piece can't move to yet,
        frame #0 won't actually move the piece!
        
        Instead, that movement SHOULD BE POST-PONED
        TO WHEN THE PIECE FINALLY GETS ROOM TO MOVE IN THAT DIRECTION.
        
        This behavior will be tested
        by holding left into a block with the I piece
        for an amount of frames from 0 and {GameControl.FIRST_DELAY - GameControl.SECOND_DELAY}
        (excluding that number),
        then moving the piece down once and checking again,
        to make sure that the moved was post-poned.

        WHILE THE DAS CHARGE HASN'T REACHED .

        THIS TEST USES THE I PIECE, BECAUSE I THOUGHT IT'S INTUITIVE TO USE FOR A TUCK TEST.
        """
        instance_2D = game_control.GameControl2D()
        instance_2D.game.piece = Piece2D(I)
        # Make sure that the I piece works I expect it to for this test
        # This position should be the same each time I create a new 'instance_2d',
        # which I must to reset the DAS, so that the test doesn't get falsified.
        self.assertEqual(
            I[0],
            [
                "    ",
                "####",
                "    ",
                "    "
            ]
        )

        X_POS_LEFT_OF_I: int = min(
            (
                square_pos[game_control.X_AXIS] - 1
                for square_pos in instance_2D.game.piece.square_positions()
            )
        )
        """
        The x_pos of the blocks that will form a wall left of the I piece,
        to test the tuck buffering
        """
        self.assertIsInstance(X_POS_LEFT_OF_I, int)

        MAX_FRAMES_WAITING_FOR_TUCK: int = game_control.GameControl.FIRST_DELAY - game_control.GameControl.SECOND_DELAY
        """
        At this frame, the game should do something different (scroll down)
        """

        for frames_waiting_for_tuck in range(MAX_FRAMES_WAITING_FOR_TUCK - 1):
            # Reset instance for next iteration
            instance_2D = game_control.GameControl2D()
            instance_2D.game.piece = Piece2D(I)
            instance_2D.game.board = {(X_POS_LEFT_OF_I, 1): (128, 128, 128)}

            for frame_waiting_for_tuck in range(frames_waiting_for_tuck):

                # The piece can't move left if there's a block there
                self.assertFalse(
                    instance_2D.direction_input_handler((LEFT, )),
                    msg=f"{frame_waiting_for_tuck=}"
                )

                # Because the piece shouldn't have moved,
                # the #0 frame move should be pending
                # (throughout all of these frames waiting for the tuck),
                # and the charge should now be 'frame_waiting_for_tuck + 1',
                # since that's the amount of frames the simulated player
                # would have been holding LEFT, and have the charge should go up
                # by one each frame.
                self.assertEqual(
                    instance_2D.das[LEFT],
                    game_control.DASSettings(True, frame_waiting_for_tuck + 1),
                    msg=f"{frame_waiting_for_tuck=}"
                )

            instance_2D.game.piece.pos[game_control.Y_AXIS] += 1

            # Check that the move WAS, INDEED, post-poned,
            # AND that the 2D instance's DAS charges
            # are still behaving like they would
            # if the piece had moved the first frame.

            # The piece should now move, since it was moved one block down,
            # and no wall should be at its left
            self.assertTrue(
                instance_2D.direction_input_handler((LEFT, )),
                msg=f"{frames_waiting_for_tuck=}"
            )

            # The DAS's charge should now be 'frame_waiting_for_tuck + 1',
            # since that's the amount of frames the simulated player
            # would have been holding LEFT, and have the charge should go up
            # by one each frame.
            self.assertEqual(
                instance_2D.das[LEFT],
                game_control.DASSettings(False, frames_waiting_for_tuck + 1),
                msg=f"{frames_waiting_for_tuck=}"
            )
