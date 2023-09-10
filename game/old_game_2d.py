"""
Module with all of the 2D piece's data (blocks, starting position, color),
the Piece2D class, meant to hold the pieces' data, rotate the piece and move the piece,
and the Game2D class, which contains the 2D game's score, the 2D game's board,
the 2D game's current and next pieces, and the amount of lines cleared the previous
"game step" (Look in 'Game2D.__init__').
"""
import random
from game.score import Score
from game.SRS_checks import SRS_CHECKS
from queue import Queue, LifoQueue

I_2D = (
    (["    ",
      "####",
      "    ",
      "    "],

     ["  # ",
      "  # ",
      "  # ",
      "  # "],

     ["    ",
      "    ",
      "####",
      "    "],

     [" #  ",
      " #  ",
      " #  ",
      " #  "]),
    (0, 255, 255))

J_2D = ((["#  ",
      "###",
      "   "],

     [" ##",
      " # ",
      " # "],

     ["   ",
      "###",
      "  #"],

     [" # ",
      " # ",
      "## "]),
     (0, 0, 255))

L_2D = ((["  #",
      "###",
      "   "],

     [" # ",
      " # ",
      " ##"],

     ["   ",
      "###",
      "#  "],

     ["## ",
      " # ",
      " # "]),
     (255, 128, 0))

O_2D = ((["##",
      "##"],),
     (255, 255, 0))

S_2D = (([" ##",
      "## ",
      "   "],

     [" # ",
      " ##",
      "  #"],

     ["   ",
      " ##",
      "## "],

     ["#  ",
      "## ",
      " # "]),
     (0, 255, 0))

T_2D = (([" # ",
      "###",
      "   "],

     [" # ",
      " ##",
      " # "],

     ["   ",
      "###",
      " # "],

     [" # ",
      "## ",
      " # "]),
     (128, 0, 255))

Z_2D = ((["## ",
      " ##",
      "   "],

     ["  #",
      " ##",
      " # "],

     ["   ",
      "## ",
      " ##"],

     [" # ",
      "## ",
      "#  "]),
     (255, 0, 0))
# Pieces data: blocks of pieces (top->bottom, left->right),
#   in all rotation configurations, clockwise,
# and their colors.

ROWS = 20
COLUMNS = 10


class Piece2D:
    """
    2D piece class with all of its rotation configurations,
    position in the board (at the top left of the piece's matrix)
    and its color.

    The rotation configurations must be matrices of list[str],
    made with # characters representing blocks, and " " characters
    representing space.
    """
    def __init__(self, piece_data: tuple[tuple[list[list[str]]], tuple[int, int, int]]):
        """
        'piece_data' should be like the ones above, like
        I_2D, J_2D, L_2D, S_2D, T_2D or Z_2D:

        all rotation configurations, IN CLOCKWISE ORDER, and their color,
        IN RGB FORMAT, IN RANGE 0 - 255.
        """
        self.all_rotations: tuple[list[list[str]]] = piece_data[0]
        self.rotation = 0

        self.pos: list = [0, 0]
        self.reset_pos()

        self.color: tuple[int, int, int] = piece_data[1]

    @property
    def piece(self):
        """
        The current rotation configuration of 'self'.
        """
        return self.all_rotations[self.rotation]

    @property    
    def piece_width(self):
        return len(self.piece[0])

    @property
    def piece_height(self):
        return len(self.piece)
    
    def reset_pos(self) -> None:
        self.pos = [(COLUMNS >> 1) - ((self.piece_width + 1) >> 1), 0]

    def relative_square_positions(self):
        """
        Returns the list of the positions of the squares
        in 'self.piece', IF 'self' WHERE IN THE TOP LEFT
        OF THE BOARD (aka, the "relative position")

        THE POSITIONS ARE RETURNED (x, y), NOT (y, x)
        """
        positions = []

        for ri, row in enumerate(self.piece):
            for ci, square in enumerate(row):

                if square == "#":
                    position = (ci, ri)
                    # They're "backwards" because the ci is the x position,
                    # and ri is the y position, and that's the order
                    # of a coordinate here, and in the window display
                    positions.append(position)
        return positions

    def square_positions(self):
        """
        Returns the list of the OBJECTIVE position all the squares of
        'self', the tetromino.

        THE POSITIONS ARE RETURNED (x, y), NOT (y, x)
        """
        positions = []

        for ri, row in enumerate(self.piece):
            for ci, square in enumerate(row):

                if square == "#":
                    position = (self.pos[0] + ci, self.pos[1] + ri)
                    positions.append(position)
        return positions


class Game2D:
    def __init__(self):
        self.pieces = [I_2D, J_2D, L_2D, O_2D, S_2D, T_2D, Z_2D]

        self.piece: Piece2D = None

        self.next_pieces: Queue = Queue(maxsize=7)
        self.next_bag: LifoQueue = LifoQueue(maxsize=7)

        self.held_piece: Piece2D = None
        self.already_held_now: bool = False

        self.spawn_next_piece()

        self.score_manager: Score = Score()

        self.board = {}
        # {pos: color}

        self.amount_of_levels_cleared: int = 0
        """
        Amount of levels (lines/floors, IN THIS CASE, LINES) the player cleared when the last piece
        landed

        Set by 'self.clear_lines', which is called RIGHT AFTER a piece lands,
        in the same game step/frame.
        """

    @property
    def next_piece(self) -> Piece2D:
        for piece in self.next_pieces.queue:
            return piece

    def handle_random_piece(self):
        """
        Post the next piece from 'self.next_pieces' into 'self.piece',
        and queues in another random piece into 'self.next_pieces'.

        If the 'self.next_pieces' queue is empty, this method replenishes it
        with a "truly random" piece sequence.

        Doesn't use 'self.next_bag'.
        """
        if self.next_pieces.empty():
            self.next_pieces.queue = [Piece2D(random.choice(self.pieces)) for _ in range(self.next_pieces.maxsize)]

        self.piece = self.next_pieces.get_nowait()
        self.next_pieces.put_nowait(Piece2D(random.choice(self.pieces)))

    def handle_7bag(self):
        """
        Pops the next piece from 'self.current_bag' into 'self.piece',
        and queues the next piece from 'self.next_bag' into 'self.current_bag'.

        If 'self.next_bag' is empty, this method replenishes it with
        a new shuffled version of 'self.pieces'.
        """

        def replenish_bag(bag: Queue | LifoQueue):
            for piece in random.sample(self.pieces, len(self.pieces)):
                bag.put_nowait(Piece2D(piece))

        if self.next_pieces.empty():
            replenish_bag(self.next_pieces)

        if self.next_bag.empty():
            replenish_bag(self.next_bag)

        self.piece = self.next_pieces.get_nowait()
        self.next_pieces.put_nowait(self.next_bag.get_nowait())

    @property
    def spawn_next_piece(self):
        return self.handle_7bag

    def try_hold(self) -> bool:
        """
        Makes 'self.held_piece' be 'self.piece',
        and makes 'self.piece' be the piece that's in 'self.held_piece' if there is one there,
        or queues in the next piece (in 'self.next_pieces') into 'self.piece', if there isn't.

        After this, this method sets 'self.already_held_now' to True.
        If 'self.already_held_now' is already True, this method won't hold.

        Returns weather or not hold succeeded.
        """
        if self.already_held_now:
            return False

        if self.held_piece:
            self.piece, self.held_piece = self.held_piece, self.piece

            # RESET THE POSITION OF THE HELD PIECE, VERY IMPORTANT:
            self.piece.pos = [
                (COLUMNS >> 1) - (self.piece.piece_width >> 1),
                0
            ]
        else:
            self.held_piece = self.piece
            self.spawn_next_piece()

        self.already_held_now = True

        return True

    def move_piece_down(self):
        self.piece.pos[1] += 1

    def try_move(self, move):
        """Tries to move piece down, and returns
        weather or not it was successfully moved.

        A piece can be successfully moved if it's
        next position (SHOULD always be one over...) 
        doesn't overlap any existing blocks in the board.

        Moves can be: LEFT, RIGHT, SOFT_DROP or HARD_DROP.
        """

        if move == "l":
            for x_pos, y_pos in self.piece.square_positions():
                if self.board.get((x_pos - 1, y_pos)) or \
                        x_pos == 0:
                    return False
            self.piece.pos[0] -= 1
            return True

        if move == "r":
            for x_pos, y_pos in self.piece.square_positions():
                if self.board.get((x_pos + 1, y_pos)) or \
                        x_pos == COLUMNS - 1:
                    return False
            self.piece.pos[0] += 1
            return True

        if move == "h":
            # If the move is a hard drop,
            while not self.landed():
                self.move_piece_down()
            return True
            # We move the piece down until it lands.

        elif move == "s" and not self.landed():
            # If the move is a soft drop, and we haven't landed,
            self.move_piece_down()
            return True
            # We move down once.

    def set_down(self):
        """
        Makes piece 'inbeded' in board.
        AKA: "puts" the squares of the piece
        in the 'self.board' dictionary.
        """
        for square_pos in self.piece.square_positions():
            self.board[square_pos] = self.piece.color

    def try_move_up(self):
        """
        Moves 'self'ss current piece up unless a square above it blocks it.
        Returns weather or not it was able to move up.
        """
        for x_pos, y_pos in self.piece.square_positions():
            if self.board.get((x_pos, y_pos - 1)):
                return False

        self.piece.pos[1] -= 1
        return True

    def rotate(self, clockwise=True):
        self.piece.rotation += 1 if clockwise else -1
        self.piece.rotation = abs(self.piece.rotation % len(self.piece.all_rotations))
        # Loops trough rotations in self.complete piece.

        # Uses mod operator to loop through piece rotations,
        # absolutes value in case they rotated counter-clockwise

    def try_rotate_SRS(self, clockwise: bool = True):
        OLD_PIECE_POS: tuple[int, int] = tuple(self.piece.pos)
        OLD_PIECE_ROTATION: int = self.piece.rotation

        self.rotate(clockwise)

        PIECE_MATRIX_SIZE = 0

        if self.piece.all_rotations[0] == I_2D[0][0]:
            PIECE_MATRIX_SIZE = 4
        elif self.piece.all_rotations[0] in (
            J_2D[0][0], L_2D[0][0], S_2D[0][0], T_2D[0][0], Z_2D[0][0]
        ):
            PIECE_MATRIX_SIZE = 3
        elif self.piece.all_rotations[0] == O_2D[0][0]:
            return [[0, 0]]
            # O doesn't need any kicks

        for check in SRS_CHECKS[PIECE_MATRIX_SIZE][OLD_PIECE_ROTATION][clockwise]:

            self.piece.pos[0] += check[0]
            self.piece.pos[1] += check[1]

            if not any(
                pos in self.board
                or pos[0] not in range(COLUMNS)
                or pos[1] not in range(ROWS)
                for pos in self.piece.square_positions()
            ):
                return True

            self.piece.pos = list(OLD_PIECE_POS)

        self.rotate(not clockwise)
        return False

    def try_rotate_raw(self, clockwise=True) -> bool:
        """
        Rotates 'self.piece'. If the piece overlaps the outside of the board
        or a square in the board, the rotation is cancelled.

        Returns True if rotation succeeded, and False if the rotation
        needed to be cancelled.
        """
        self.rotate(clockwise)

        if any(
            pos in self.board
            or pos[0] not in range(COLUMNS)
            or pos[1] not in range(ROWS)
            for pos in self.piece.square_positions()
        ):
            self.rotate(not clockwise)

            return False
        return True

    @property
    def try_rotate(self):
        return self.try_rotate_SRS

    def landed(self):
        """
        Checks if 'self's current piece landed.
        A piece has landed if the floor or
        another square is EXACTLY one square below
        one of the piece's squares.
        """
        for square_pos in reversed(self.piece.square_positions()):
            # 'self.piece.square_positions' returns all of the squares
            # in order: up->down, left->right.
            # We want to scan down->up.
            if self.board.get((square_pos[0], square_pos[1] + 1)) or \
                    square_pos[1] == ROWS - 1:
                # If there's a block or the wall underneath it...
                # Return True.
                return True
        return False

    def landing_handler(self):
        """If a piece landed, marks it at the previous piece,
        makes it part of the board, and spawns a new one."""
        if self.landed():
            self.set_down()
            self.clear_lines(self.piece)
            self.spawn_next_piece()

    def clear_lines(self, previous_piece: Piece2D) -> int:
        """
        Finds every row in 'previous_piece', ASSUMING THAT
        'previous_piece' IS THE PIECE THAT JUST LANDED,
        and clears all of the lines it completes.

        Stores the amount of lines the player just cleared
        in 'self.amount_of_lines_cleared'.
        """
        # time: O(n), where n is: height of piece
        # space: O(n), where n is: height of piece
        deleted_rows = set()

        for y_pos, row in zip(range(len(previous_piece.piece), 0, -1), previous_piece.piece):
            # look at each row in the dropped piece
            square_y_pos = self.piece.pos[1] + len(self.piece.piece) - y_pos

            for x_pos in range(COLUMNS):
                if not ((x_pos, square_y_pos) in self.board):
                    break
            else:
                # If the whole row in the board is filled
                for x_pos in range(COLUMNS):
                    self.board.pop((x_pos, square_y_pos))
                # remove that row
                deleted_rows.add(square_y_pos)
                # keep track of that row

        landing_row = 0
        for row in deleted_rows:
            if row > landing_row:
                landing_row = row
        # lowest deleted row is where all the rows with gunk in them will 'land' on.

        gunk_row = landing_row - 1
        while gunk_row > -1:
            if not (gunk_row in deleted_rows):
                # if row has gunk in it
                for x_pos in range(COLUMNS):
                    if (x_pos, gunk_row) in self.board:
                        self.board[(x_pos, landing_row)] = self.board.pop((x_pos, gunk_row))
                # move that row down to the landing row

                landing_row -= 1
            gunk_row -= 1
        
        self.amount_of_levels_cleared = len(deleted_rows)
        self.score_manager.score(self.amount_of_levels_cleared)

    def play(self):
        """
        Plays Tetris for one "step" (where the piece goes one down),
        and returns True if the game can continue,
        and False it the game is over.

        This is the "step":
        If the current piece has landed,
        we set it down using 'self.set_down',
        clear any lines the piece completed with 'self.clear_lines'
        and makes a new piece.
        
        If the new piece spawns where it immediately lands,
        the game is over.

        If the piece hasn't landed, or if the game isn't over,
        we just move the piece one down using
        'self.move_piece_down'.
        """
        if self.landed():
            self.set_down()
            self.clear_lines(self.piece)
            self.spawn_next_piece()

            self.already_held_now = False

            if any(
                block in self.board
                for block in self.piece.square_positions()
            ):
                return False
        else:
            self.move_piece_down()

        return True
