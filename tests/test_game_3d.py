from game import game_3d
from numpy import rot90
import unittest


class TestPiece3D(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pieces = [game_3d.Piece3D(*piece_data) for piece_data in game_3d.PIECES_3D]

    def test_rotate(self):
        for piece in self.pieces:
            for rotation_axis in range(3):
                for direction in (True, False):
                    piece.rotate(rotation_axis, direction)
                    expected_piece_blocks = rot90(piece.blocks, 1 if direction else 3, (axis for axis in range(3) if axis != rotation_axis))
                    self.assertTrue(
                        all(
                            block in piece.blocks
                            for block in expected_piece_blocks
                        )
                    )

    def test_relative_block_positions(self):
        """
        The whole point of Piece3D.relative_block_positions
        is the position of all 1's in the numpy.ndarray,
        meant to represent the piece in 2D as a cube of empty or "full"
        cubes.

        This method tests that the Piece3D.relative_block_positions method
        outputs the correct relative positions of all the cubes iniside
        its piece,
        
        by looking-up each individual position and seeing if the
        int in the 3D numpy.ndarray is a 1.
        
        THE TEST SUCCEEDS IF ALL OF THEM ARE.
        """
        for piece in self.pieces:
            for relative_cube_pos in piece.relative_block_positions():
                self.assertEqual(piece.blocks[relative_cube_pos[0], relative_cube_pos[1], relative_cube_pos[2]], 1)

    def test_block_positions(self):
        """
        The "objective" position of the cubes in a 3D piece
        are their position relative to the top-fron-left corner,
        plus the position of that corner in-board.
        (PLEASE LOOK AT THE DOCUMENTATION IN '.../Tetris3D/game/game_3d.py')
        
        This test succeeds if all of the positions returned by
        'Piece3D.block_positions' "shifted" to position (0, 0, 0)
        match the RELATIVE positions of the blocks
        
        (see test above)
        """
        for piece in self.pieces:
            PIECE_AT_ORIGIN = game_3d.Piece3D(piece.blocks.copy(), piece.color)
            PIECE_AT_ORIGIN.pos = [0, 0, 0]

            self.assertEqual(PIECE_AT_ORIGIN.relative_block_positions(), PIECE_AT_ORIGIN.block_positions())


class TestGame3D(unittest.TestCase):
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

        self.game.init_random_piece()
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
        self.game.move_piece_down()
        self.assertTrue(self.game.piece.pos[2] == OLD_PIECE_Z_POS + 1)

    def test_try_move(self):
        """
        'self.game.try_move' should move ONE cube of distance
        in any direction in the board,
        
        ONLY if the new piece's blocks' positions
        aren't already occupied by any blocks
        in the board, or any of the piece's blocks go outside
        the ranges of the board.

        We can test this by putting a new block in the board
        in front of the front-most block in the piece, relative
        to the direction it's about to move in,
        then testing if the piece overlaps it or not.

        AND run another string of tests where we put the piece at the edge of the board,
        then see if any of the piece's blocks go outside of it.

        AND A FINAL TEST that tries to move a piece with no blocks in its way,
        and make sure it ACTUALLY MOVES.
        """
        pass
