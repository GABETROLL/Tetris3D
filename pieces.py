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

LEFT = "l"
RIGHT = "r"
HARD_DROP = "h"
SOFT_DROP = "s"


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


class Board:
    def __init__(self):
        self.pieces = [I, J, L, O, S, T, Z]
        self.init_random_piece()

        self.board = {}
        # {(5, 4):(255, 0, 0)}

    def init_random_piece(self):
        self.piece = Piece(random.choice(self.pieces))
        """piece player can currently control. (piece data, pos)"""

    def move_piece_down(self):
        self.piece.pos[1] += 1

    def try_move(self, move):
        """Tries to move piece down.

        Moves can be: LEFT, RIGHT, SOFT_DROP or HARD_DROP."""
        split_piece = self.piece.piece.split("\n")

        if move == "l" and self.piece.pos[0] > 0:
            will_move = True
            for ri, row in enumerate(split_piece):
                for ci, square in enumerate(row):
                    if square == "#" and self.board.get((self.piece.pos[0] + ci - 1, self.piece.pos[1] + ri)):
                        will_move = False

            if will_move:
                self.piece.pos[0] -= 1

        if move == "r" and self.piece.pos[0] < COLUMNS - len(split_piece[0]):
            will_move = True
            for ri, row in enumerate(split_piece):
                for ci, square in enumerate(row):
                    if square == "#" and self.board.get((self.piece.pos[0] + ci + 1, self.piece.pos[1] + ri)):
                        will_move = False

            if will_move:
                self.piece.pos[0] += 1
        # If the piece has a square in the board left or right of one of its squares,
        # We can't move there.

        if move == "h":
            # If the move is a hard drop,
            while not self.landed():
                self.move_piece_down()
            # We move the piece down until it lands.

        if move == "s" and not self.landed():
            # Id the move is a soft drop and we haven't landed,
            self.move_piece_down()
            # We move down once.

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

    def rotate(self, clockwise=True):
        self.piece.rotation += 1 if clockwise else -1
        self.piece.rotation = abs(self.piece.rotation % len(self.piece.all_rotations))
        # Loops trough rotations in self.complete piece.

        # Uses mod operator to loop through piece rotations,
        # absolutes value in case they rotated counter-clockwise

    def landed(self):
        """Checks if the piece landed."""
        split_piece = self.piece.piece.split("\n")
        for ypos, row in enumerate(split_piece):
            for xpos, square in enumerate(row):
                # Check every square in the piece's bottom row.
                if square == "#":
                    if self.board.get((xpos + self.piece.pos[0], self.piece.pos[1] + ypos + 1)) or \
                            self.piece.pos[1] + len(self.piece.piece.split("\n")) == ROWS:
                        # If there's a square in the board under a square in the piece...
                        print(xpos, (xpos + self.piece.pos[0], self.piece.pos[1] + len(split_piece)))
                        return True
        return False

    def landing_handler(self):
        if self.landed():
            self.set_down()
            self.init_random_piece()

    def play(self):
        self.landing_handler()
        self.move_piece_down()
