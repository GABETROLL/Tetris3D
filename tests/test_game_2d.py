from game import game_2d
from PIL import Image
from itertools import chain
import unittest


def opaque_color(color: tuple[int, int, int]):
    return tuple((channel >> 1) for channel in color)


def draw_piece(image: Image, piece: game_2d.Piece2D, opaque=False):
    for block_pos in piece.square_positions():
        image.putpixel(
            tuple(block_pos),
            opaque_color(piece.color) if opaque else piece.color
        )


PIECE_ROWS = 4
PIECE_COLUMNS = 10

game = game_2d.Game2D()

PIECES = game.pieces
PIECES.remove(game_2d.O_2D)


for piece_num, piece in enumerate(game.pieces):
    piece = game_2d.Piece2D(piece)

    game.piece = piece

    PIECE_MATRIX_SIZE = len(piece.all_rotations[0])
    PIECE_TILE_SIZE = PIECE_MATRIX_SIZE + 4

    piece_image = Image.new('RGB', (PIECE_COLUMNS * PIECE_TILE_SIZE, PIECE_ROWS * PIECE_TILE_SIZE))

    for initial_rotation in range(4):
        piece_drawing_column_pos = 0

        CHECK_FAMILY = game_2d.SRS_CHECKS[PIECE_MATRIX_SIZE][initial_rotation]

        for clockwise in (False, True):

            if not clockwise:
                SRS_CHECKS = tuple(reversed(CHECK_FAMILY[False]))
            else:
                SRS_CHECKS = CHECK_FAMILY[True]

            # print(piece_num, piece, initial_rotation, clockwise, SRS_CHECKS)

            for SRS_CHECK in SRS_CHECKS:

                piece.rotation = initial_rotation
                piece.pos = [piece_drawing_column_pos * PIECE_TILE_SIZE + 2, initial_rotation * PIECE_TILE_SIZE + 2]

                draw_piece(piece_image, piece, opaque=True)
                # DRAW PIECE IN ITS INITIAL STATE BEFORE ROTATION,
                # BEHIND THE SRS CHECK DRAWING, OPAQUE

                game.rotate(clockwise=clockwise)

                # print(f"{piece.rotation = }")

                # print(piece.pos)

                piece.pos[0] += SRS_CHECK[0]
                piece.pos[1] += SRS_CHECK[1]

                draw_piece(piece_image, piece)

                piece_drawing_column_pos += 1
    
    piece_image.save(f"tests/SRS_check_tests/{piece_num}_SRS_checks.png")


class TestBag(unittest.TestCase):
    def test_random_piece(self):
        """
        Tests that 'game_2d.handle_random_piece' makes
        'game.piece' now be 'game.next_piece',
        that the next piece in 'instance.next_pieces'
        has been queued into 'instance.piece',
        and that 'instance.next_pieces' now has a new
        random piece.
        """
        instance = game_2d.Game2D()

        OLD_NEXT_PIECE = instance.next_piece
        OLD_NEXT_PIECES = list(instance.next_pieces.queue)

        instance.handle_random_piece()

        self.assertIs(OLD_NEXT_PIECE, instance.piece)
        self.assertEqual(OLD_NEXT_PIECES[1:], list(instance.next_pieces.queue)[:-1])

    def test_7bag(self):
        instance = game_2d.Game2D()

        print(dir(instance))

        old_next_bag: list = None

        for _ in range(len(instance.pieces)):

            OLD_NEXT_PIECE = instance.next_piece
            OLD_NEXT_PIECES = list(instance.next_pieces.queue)
            old_next_bag = list(instance.next_bag.queue)

            instance.handle_7bag()

            self.assertIs(OLD_NEXT_PIECE, instance.piece)
            self.assertEqual(OLD_NEXT_PIECES[1:], list(instance.next_pieces.queue)[:-1])

        self.assertEqual(old_next_bag, [])

        instance.handle_7bag()

        self.assertFalse(instance.next_pieces.empty())
