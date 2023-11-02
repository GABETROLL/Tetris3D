from game import game_3d
from numpy import rot90, nditer
import unittest
from itertools import combinations


GREY = (128, 128, 128)


def piece_inside_board(piece: game_3d.Piece3D):
    return all(
        pos[0] in range(game_3d.FLOOR_WIDTH)
        and pos[1] in range(game_3d.FLOOR_WIDTH)
        and pos[2] in range(game_3d.FLOORS)
        for pos in piece.block_positions()
    )


def piece_overlaps_board_blocks(game: game_3d.Game3D):
    """
    Returns True if ANY of the game's piece's blocks
    are ALSO found in the game's board.
    """
    return any(block in game.board for block in game.piece.block_positions())


class TestPiece3D(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pieces = [game_3d.Piece3D(*piece_data)
                       for piece_data in game_3d.PIECES_3D]

    def test_piece_inits_inside_board(self):
        """
        Creating a new game_3d.Piece instance should always
        initialize the piece INSIDE the board.

        AKA: all of the piece's block_positions
        are within the range of game_3d.FLOORS
        and game_3d.FLOOR_WIDTH, respective to the axii.
        """
        for piece in self.pieces:
            self.assertTrue(
                piece_inside_board(piece)
            )

    # TODO: REDUNDANT
    def test_rotate(self):
        for piece in self.pieces:
            for rotation_axis in range(3):
                for direction in (True, False):
                    piece.rotate(rotation_axis, direction)
                    expected_piece_blocks = rot90(
                        piece.blocks, 1 if direction else 3, (axis for axis in range(3) if axis != rotation_axis))
                    self.assertTrue(
                        all(
                            block in piece.blocks
                            for block in expected_piece_blocks
                        )
                    )

    def test_relative_block_positions(self):
        """
        'Piece3D.relative_block_positions' returns
        the position of all 1's in the numpy.ndarray,
        meant to represent the piece in 2D as a cube of empty or "full"
        cubes.

        This method tests that the Piece3D.relative_block_positions method
        outputs the correct relative positions of all the cubes iniside
        its piece,

        by looking-up each individual position and seeing if the
        int in the 3D numpy.ndarray is a 1,

        and by checking if all of the 1's have been found.

        THE TEST SUCCEEDS IF ALL OF THEM ARE.
        """
        for piece in self.pieces:
            BLOCK_POSITIONS = piece.relative_block_positions()
            # make sure all of the positions are 1's
            for relative_cube_pos in BLOCK_POSITIONS:
                self.assertEqual(
                    piece.blocks[relative_cube_pos[0], relative_cube_pos[1], relative_cube_pos[2]], 1)

            self.assertEqual(len(BLOCK_POSITIONS), sum(nditer(piece.blocks)))

    def test_block_positions(self):
        """
        The "objective" position of the cubes in a 3D piece
        are their position relative to the top-fron-left corner,
        plus the position of that corner in-board.
        (PLEASE LOOK AT THE DOCUMENTATION IN '.../Tetris3D/game/game_3d.py')

        This test succeeds if all of the positions returned by
        'Piece3D.block_positions' "shifted" to position (0, 0, 0)
        match the RELATIVE positions of the blocks

        AND if the amount of positions returned corresponds to the amount
        of 1's in the piece.

        (see test above)
        """
        for piece in self.pieces:
            PIECE_AT_ORIGIN = game_3d.Piece3D(piece.blocks.copy(), piece.color)
            PIECE_AT_ORIGIN.pos = [0, 0, 0]

            BLOCK_POSITIONS = PIECE_AT_ORIGIN.block_positions()

            self.assertEqual(
                PIECE_AT_ORIGIN.relative_block_positions(), BLOCK_POSITIONS)

            self.assertEqual(len(BLOCK_POSITIONS), sum(nditer(piece.blocks)))


class TestGame3D(unittest.TestCase):
    """
    There are only a few ways to try to alter any state in Game3D:
    - make 'game.piece' point to 'game.next_piece'                     DONE
        and init a new 'game.next_piece, using 'game.next_piece'
    - try to move a piece with nothing in its way        (AND SUCCEED) DONE
    - try to move a piece with a block in its way        (AND FAIL)    DONE
    - try to move a piece with a wall/floor in its way   (AND FAIL)    DONE
    (all of these using 'game.try_move')
    - try to rotate a piece with nothing in its way      (AND SUCCEED) DONE
    - try to rotate a piece with a block in its way      (AND FAIL)    DONE
    - try to rotate a piece with a wall/floor in its way (AND FAIL)    DONE
    (all of these using 'game.try_rotate')
    - inbed the game's piece into its board using 'game.set_down'      DONE
    - move the game's piece with 'game.move_piece_down' (redundant)    DONE

    - TODO: test 'game.clear_lines'

    - AND check that a piece CAN NEVER MOVE UP. TODO

    And there's a few expected inputs and outputs:
    - 'try_move' should output True when the piece move (mentioned above)               DONE
        succeeds, and False when it fails
    - 'landed' should output True if anything (block or floor) is below                 DONE
        the game's current piece
    - 'play' should return True if the game can continue, or False if the game is over  TODO
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = game_3d.Game3D()

    def test_init_random_piece(self):
        """
        'self.game.init_random_piece' should make 'self.game.piece'
        be 'self.game.next_piece', and make
        a new, random 'self.game.next_piece',
        with the data in 'game_3d.PIECES_3D'.
        """
        # 'self.game.piece' is what was in 'self.game.next_piece'
        OLD_PIECE = self.game.piece
        OLD_NEXT_PIECE = self.game.next_piece

        self.game._init_random_piece()
        self.assertIs(self.game.piece, OLD_NEXT_PIECE)
        # 'self.game.next_piece' is brand new
        self.assertIsNot(self.game.next_piece, OLD_NEXT_PIECE)
        self.assertIsNot(self.game.next_piece, OLD_PIECE)

    def test_move_piece_down(self):
        """
        Tests that 'self.game.move_piece_down' adds 1
        to 'self.game.piece.pos[2]' (AKA
        'self's game's piece's Z-position)
        """
        OLD_PIECE_Z_POS = self.game.piece.pos[2]
        self.game._move_piece_down()
        self.assertTrue(self.game.piece.pos[2] == OLD_PIECE_Z_POS + 1)

    def test_try_move(self):
        """
        'self.game.try_move' should move 'self.game.piece'
        ONE cube of distance in any direction in the board
        (that's one of these: LEFT, RIGHT, FRONT, BACK, SOFT_DROP),

        ONLY if there's no wall, floor or block in the board
        that's in the piece's way.

        If the piece could be moved, 'self.game.try_move' should return True,
        and the piece's new position should be the predicted.
        Otherwise, 'self.game.try_move' should return False, and the piece's
        position should be the same as before.

        The piece's position, no matter what, SHOULD ALWAYS be inside the board,
        and SHOULD NEVER overlap any blocks in the board.

        TESTS:
        put a new block in the board right beside where the piece
        is going to move, then try to move the piece in that direction.
        THE MOVE SHOULD FAIL.

        move the piece until it reaches each face in the board (EXCEPT ABOVE),
        and check that the piece move SUCCEEDS when the piece can move in that direction
        without going outsite the board, and FAILS when the piece could leave.
        """
        MOVES = ((game_3d.RIGHT, game_3d.LEFT),
                 (game_3d.BACK, game_3d.FRONT), (game_3d.SOFT_DROP))

        for piece in game_3d.PIECES_3D:
            # first test (read docstring)
            self.game.piece = game_3d.Piece3D(*piece)
            self.game.board = {}
            # start with empty board to prevent any stray blocks
            # falsify the tests

            # TEST: moving any piece in any way SHOULD FAIL
            # if a block in the board is in its way,
            # by returning False and keeping the piece's position the same.

            # note that some of these blocks "in the way" of the piece's moves
            # may actually be outisde the board! This shouldn't matter, though,
            # because we'll test that the pieces can't go outside the board either.
            for axis, moves in enumerate(MOVES):
                for reverse, direction, move in zip((True, False), (1, -1), moves):
                    SORTED_PIECE_BLOCKS = sorted(self.game.piece.block_positions(
                    ), key=lambda block_pos: block_pos[axis], reverse=reverse)

                    EDGE_MOST_BLOCKS = (
                        block_pos
                        for block_pos in SORTED_PIECE_BLOCKS
                        if block_pos[axis] == SORTED_PIECE_BLOCKS[0][axis]
                    )
                    """
                    All of the blocks right in front of the piece, in the direction
                    we'll try to move it
                    """

                    for edge_most_block in EDGE_MOST_BLOCKS:
                        self.game.board = {}
                        # empty board to prevent any stray blocks
                        # falsify the tests

                        obstacle_block_pos = list(edge_most_block)
                        obstacle_block_pos[axis] += direction
                        self.game.board[tuple(obstacle_block_pos)] = GREY

                        self.assertTrue(piece_inside_board(self.game.piece))
                        self.assertFalse(
                            piece_overlaps_board_blocks(self.game))
                        # assert piece is completely inside board
                        # and doesn't overlap any blocks in the board

                        PREVIOUS_PIECE_POS = self.game.piece.pos.copy()
                        self.assertFalse(self.game.try_move(move))
                        # assert 'try_move' returns False when move fails
                        self.assertEqual(PREVIOUS_PIECE_POS,
                                         self.game.piece.pos)
                        # assert piece didn't move

                        self.assertTrue(piece_inside_board(self.game.piece))
                        self.assertFalse(
                            piece_overlaps_board_blocks(self.game))
                        # assert piece is completely inside board
                        # and doesn't overlap any blocks in the board

            # TEST: any piece moved in any way should SUCCEED if
            # no wall/floor (or block, see above) is in its way,
            # and FAIL when a wall/floor is.
            self.game.piece = game_3d.Piece3D(*piece)
            self.game.board = {}
            # start with empty board to prevent any stray blocks
            # falsify the tests

            for axis, moves in enumerate(MOVES):
                for direction, move in zip((1, -1), moves):
                    while True:
                        self.assertTrue(piece_inside_board(self.game.piece))
                        self.assertFalse(
                            piece_overlaps_board_blocks(self.game))
                        # assert piece is completely inside board
                        # and doesn't overlap any blocks in the board

                        PREVIOUS_PIECE_POS = self.game.piece.pos.copy()

                        self.game.piece.pos[axis] += direction
                        PIECE_WOULD_LEAVE = not piece_inside_board(
                            self.game.piece)
                        self.game.piece.pos[axis] -= direction

                        MOVE_RESULT = self.game.try_move(move)

                        self.assertTrue(piece_inside_board(self.game.piece))
                        self.assertFalse(
                            piece_overlaps_board_blocks(self.game))
                        # assert piece is completely inside board
                        # and doesn't overlap any blocks in the board

                        if PIECE_WOULD_LEAVE:
                            self.assertFalse(MOVE_RESULT)
                            # a failed move in 'self.game.try_move' should return False.
                            self.assertEqual(
                                PREVIOUS_PIECE_POS, self.game.piece.pos)
                            # assert the piece never moved,
                            # if any of its blocks would leave the board.
                            break
                            # Piece reached the wall and can no longer move,
                            # so we can start testing the next piece.
                        else:
                            self.assertTrue(MOVE_RESULT)
                            self.assertNotEqual(
                                PREVIOUS_PIECE_POS, self.game.piece.pos)
                            # a successful move in 'self.game.try_move' should return True,
                            # and change the piece's position
                            EXPECTED_PIECE_DESTINATION = PREVIOUS_PIECE_POS.copy()
                            EXPECTED_PIECE_DESTINATION[axis] += direction
                            self.assertEqual(
                                self.game.piece.pos, EXPECTED_PIECE_DESTINATION)
                            # assert piece moved to its expected destination

            # test HARD_DROP
            self.game.piece = game_3d.Piece3D(*piece)

            self.game.try_move(game_3d.HARD_DROP)
            self.assertTrue(self.game.landed())

        self.game.piece.pos = []

    def test_try_rotate(self):
        """
        'self.game.try_rotate' should always rotate a piece when
        nothing is in its way, and never when a block
        in 'self.game.board' overlaps the piece or
        any of the piece's blocks go outside the board
        once it finishes rotating.

        We can test this by:
        - Rotating every piece (which SHOULD to fit in the board,
            see Piece3D tests) in every way possible, 3 at a time
        - moving each piece to each face, edge and corner,
            rotating it in every way possible, 3 at a time again,
            and testing that:

            the rotation SUCCEEDS when the piece can stay in the board
            after rotating
            - OR -
            the rotation FAILS when the piece leaves the board after
            rotating
        - filling the board with a grey block in each
            position the piece would rotate into (exculsively), then checking that
            the rotation failed, and that the board and piece stayed the same.
        """
        for piece in game_3d.PIECES_3D:
            self.game.board = {}
            # empty board to prevent falsified tests
            # (it'll still be empty when it gets to the obstacle test)

            # try to rotate 'self.game.piece'
            # in all 6 ways possible
            # (3 axii * 2 directions (clockwise / counterclockwise)),
            # 3 at a time, starting from the piece's default rotation.

            # since all of the pieces in 'game_3d.PIECES_3D's matrices
            # fit completely inside the board,
            # we should be able to rotate them all successfully.
            for axii in combinations(range(3), 1):
                self.game.piece = game_3d.Piece3D(*piece)

                for axis in axii:
                    for clockwise in (True, False):

                        self.assertTrue(
                            self.game.try_rotate(axis, clockwise),
                            msg=f"{self.game.piece.color=} {axis=} {clockwise=} {self.game.board=}"
                        )

            self.game.piece = game_3d.Piece3D(*piece)
            # reset piece to prevent tests being falsified

            # ALL OF THESE MOVES ARE ALSO TESTED, LOOK ABOVE
            # move all of the pieces to each face edge and corner (except the ones above the board)
            for perpendicular_faces_moves in ((game_3d.LEFT, game_3d.RIGHT), (game_3d.FRONT, game_3d.BACK), (game_3d.HARD_DROP)):
                for face_move in perpendicular_faces_moves:
                    # move piece to face
                    # (if we're moving the piece to the second face,
                    # which should be perpendicular to the first
                    # (defined in this for-loop, look above),
                    # we should have the piece in the corner)
                    while True:
                        PREVIOUS_PIECE_POS = self.game.piece.pos
                        self.game.try_move(face_move)
                        if PREVIOUS_PIECE_POS == self.game.piece.pos:
                            break

                    for axii in combinations(range(3), 1):
                        self.game.piece = game_3d.Piece3D(*piece)

                        for axis in axii:
                            for clockwise in (True, False):

                                self.game.piece.rotate(axis, clockwise)
                                PIECE_WOULD_LEAVE_BOARD = any(
                                    x_pos not in range(game_3d.FLOOR_WIDTH)
                                    or y_pos not in range(game_3d.FLOOR_WIDTH)
                                    or z_pos not in range(game_3d.FLOORS)
                                    for x_pos, y_pos, z_pos in self.game.piece.block_positions()
                                )
                                self.game.piece.rotate(axis, not clockwise)
                                # rotate, then undo to see if the rotation would make the piece
                                # leave the board

                                if PIECE_WOULD_LEAVE_BOARD:
                                    PREVIOUS_PIECE_BLOCKS = self.game.piece.block_positions()
                                    self.game.try_rotate(axis, clockwise)
                                    self.assertEqual(
                                        PREVIOUS_PIECE_BLOCKS, self.game.piece.block_positions())

            self.game.board = {}
            # empty board to prevent tests being falsified

            for axis in range(3):
                for clockwise in (True, False):
                    PIECE_BLOCK_POSITIONS = self.game.piece.block_positions()
                    self.game.piece.rotate(axis, clockwise)
                    rotation_obstacles = (
                        pos
                        for pos in self.game.piece.block_positions()
                        if pos not in PIECE_BLOCK_POSITIONS
                    )
                    # all of the blocks would stop the piece's currently tested rotation,
                    # that don't interfere with the piece's current position
                    # (we rotate and un-rotate to figure these blocks out)
                    self.game.piece.rotate(axis, not clockwise)

                    for rotation_obstacle in rotation_obstacles:
                        self.game.board = {rotation_obstacle: GREY}
                        PRE_ROTATION_BOARD = self.game.board.copy()

                        self.assertFalse(self.game.try_rotate(axis, clockwise))
                        # rotation must fail, if we put all the blocks properly.
                        self.assertEqual(PIECE_BLOCK_POSITIONS,
                                         self.game.piece.block_positions())
                        # if the rotation fails, its blocks must stay the same.
                        self.assertEqual(self.game.board, PRE_ROTATION_BOARD)

    def test_set_down(self):
        """
        Tests that 'self.game.set_down' copies the blocks in 'self.game.piece'
        to 'self.game.board', with the piece's color as the value and the block
        positions as the keys.
        """
        for piece in game_3d.PIECES_3D:
            self.game.piece = game_3d.Piece3D(*piece)
            self.game.set_down()

            for block_pos in self.game.piece.block_positions():
                self.assertEqual(
                    self.game.board[block_pos], self.game.piece.color)

    def test_landed(self):
        """
        Tests that 'self.game.landed' returns True if 'self.game.piece'
        has a cube that's directly above a cube in 'self.game.board',
        or the board's floor.

        It does that by placing a GREY (placeholder value) block in 'self.game.board',
        one cube below each cube in 'self.game.piece' that's the lowest in its piece in its column,
        then checking that 'self.game.landed()' == True.
        """
        for piece in game_3d.PIECES_3D:
            self.game.piece = game_3d.Piece3D(*piece)

            # Test that 'self.game.landed()' returns True when the piece is at the bottom of the board:
            # (while loop moves the piece to the bottom of the board)
            while not any(z_pos == game_3d.FLOORS - 1 for (_, _, z_pos) in self.game.piece.block_positions()):
                self.game._move_piece_down()  # already tested, scroll up
            # assert
            self.assertTrue(self.game.landed())

            PIECE_BLOCKS = set(self.game.piece.block_positions())

            for block_pos in PIECE_BLOCKS:
                LANDING_BLOCK_POS = block_pos[0], block_pos[1], block_pos[2] + 1

                if LANDING_BLOCK_POS in PIECE_BLOCKS:
                    continue

                self.game.board = {LANDING_BLOCK_POS: GREY}

                self.assertTrue(self.game.landed())

            # hard-drop test
            self.game.board = {}
            self.game.try_move(game_3d.HARD_DROP)
            self.assertTrue(self.game.landed())

    def test_clear_floors(self):
        """
        Tests that all of the complete floors get cleared,
        using every piece, with all of the floors it occupies
        being filled out with 'GREY'-colored blocks.
        """
        for piece in game_3d.PIECES_3D:
            self.game.piece = game_3d.Piece3D(*piece)

            PIECE_BLOCK_POSITIONS = self.game.piece.block_positions()
            PIECE_FLOORS = set(z_pos for (_, _, z_pos)
                               in self.game.piece.block_positions())
            self.game.board = {
                (x_pos, y_pos, z_pos): self.game.piece.color
                for x_pos in range(game_3d.FLOOR_WIDTH)
                for y_pos in range(game_3d.FLOOR_WIDTH)
                for z_pos in PIECE_FLOORS
                if (x_pos, y_pos, z_pos) not in PIECE_BLOCK_POSITIONS
            }

            self.game.set_down()
            self.game._clear_floors(self.game.piece)

            self.assertEqual(self.game.board, {})

    def test_play(self):
        """
        Tests that:
        If the game's current piece hasn't landed yet,
        'self.game.play' always returns True.
        """
        for piece in game_3d.PIECES_3D:
            self.game.board = {}
            self.game.piece = game_3d.Piece3D(*piece)

            self.assertTrue(self.game.play())
