import random

START_POS = [3, 0]

I = ("####",
     "#\n#\n#\n#",
     START_POS,
     (0, 255, 255))

J = ("#  \n###",
     "##\n# \n# ",
     "###\n  #",
     " #\n #\n##",
     START_POS,
     (0, 0, 255))

L = ("  #\n###",
     "# \n# \n##",
     "###\n#  ",
     "##\n #\n #",
     START_POS,
     (255, 128, 0))

O = ("##\n##",
     [4, 0],
     (255, 255, 0))

S = (" ##\n## ",
     "# \n##\n #",
     START_POS,
     (0, 255, 0))

T = (" # \n###",
     "# \n##\n# ",
     "###\n # ",
     " #\n##\n #",
     START_POS,
     (128, 0, 255))

Z = ("## \n ##",
     " #\n##\n# ",
     START_POS,
     (255, 0, 0))
# Pieces data. Line-by-line data of piece's squares. Start positions and colors.

ROWS = 20
COLUMNS = 10


class Piece:
    def __init__(self, piece: tuple):
        piece = list(piece)
        self.pos = list(piece.pop(-2))
        self.color = piece.pop(-1)
        self.all_rotations = piece
        self.rotation = 0

    @property
    def piece(self):
        return self.all_rotations[self.rotation]

    def move_down(self):
        self.pos[1] += 1

    def rotate(self, clockwise=True):
        self.rotation += 1 if clockwise else -1
        self.rotation = abs(self.rotation % len(self.all_rotations[:-2]))
        # Loops trough rotations in self.complete piece.

        # Uses mod operator to loop through piece rotations,
        # absolutes value in case they rotated counter-clockwise


class Board:
    def __init__(self):
        self.pieces = [I, J, L, O, S, T, Z]
        self.init_random_piece()

        self.board = {}
        # {(5, 4):(255, 0, 0)}

    def init_random_piece(self):
        self.piece = Piece(random.choice(self.pieces))
        """piece player can currently control. (piece data, pos)"""

    def set_down(self):
        """Makes piece inbeded in board."""
        split_piece = self.piece.piece.split("\n")
        # Splits pieces format row by row.

        for ri, row in zip(range(self.piece.pos[1], self.piece.pos[1] + len(split_piece)), split_piece):
            for ci, square in zip(range(self.piece.pos[0], self.piece.pos[0] + len(row)), row):
                # We iterate over both the positions of the squares in the piece
                # Based on it's position and each square,
                # row by row, column by column,

                if square == "#":
                    self.board[(ci, ri)] = self.piece.color
                    # And append the squares to the board.

    def landed(self):
        split_piece = self.piece.piece.split("\n")
        for xpos, square in enumerate(self.piece.piece.split("\n")):
            # Check every square in the piece's bottom row.
            if self.board.get((xpos + self.piece.pos[0], self.piece.pos[1] + len(split_piece))):
                # If there's a square in the board under it,
                self.set_down()
                self.init_random_piece()

    def play(self):
        self.landed()

        if self.piece.pos[1] + len(self.piece.piece.split("\n")) == ROWS:
            # If the piece is touching the bottom,
            self.set_down()
            # We inbbed the current piece to the board as individual blocks,
            self.init_random_piece()
            # And make a new piece.
        else:
            self.piece.move_down()
