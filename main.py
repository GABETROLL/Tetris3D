import pygame
from pieces import *

GREY = (128, 128, 128)
BLACK = (0, 0, 0)

RAINBOW = [(255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255)]


class Window:
    def __init__(self, width, height, board_width):
        self.WIDTH = width
        self.HEIGHT = height

        self.BOARD_WIDTH = board_width
        self.BOARD_HEIGHT = board_width * 2

        self.WINDOW = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.running = True

        self.fps = 60

        self.game = Board()

        self.fall_rate = 60

        self.rotated_clockwise = False
        self.rotated_counter_clockwise = False

        while self.running:
            for frame in range(self.fall_rate):
                self.clock.tick(self.fps)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False

                self.WINDOW.fill(BLACK)

                self.draw_board()
                self.draw_piece()

                self.input_handler()

                pygame.display.update()
            self.game.play()

        pygame.quit()

    def input_handler(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.game.try_move(LEFT)
        if keys[pygame.K_s]:
            self.game.try_move(SOFT_DROP)
        if keys[pygame.K_d]:
            self.game.try_move(RIGHT)

        if keys[pygame.K_SPACE]:
            self.game.try_move(HARD_DROP)

        if keys[pygame.K_PERIOD] and not self.rotated_clockwise:
            self.game.rotate()
            self.rotated_clockwise = True
        elif self.rotated_clockwise and not keys[pygame.K_PERIOD]:
            self.rotated_clockwise = False

        if keys[pygame.K_COMMA] and not self.rotated_counter_clockwise:
            self.game.rotate(False)
            self.rotated_counter_clockwise = True
        elif self.rotated_counter_clockwise and not keys[pygame.K_COMMA]:
            self.rotated_counter_clockwise = False


    @property
    def board_pos(self):
        """returns (xpos, ypos) of the board."""
        return self.WIDTH // 2 - self.BOARD_WIDTH // 2, self.HEIGHT // 2 - self.BOARD_HEIGHT // 2

    @property
    def block_width(self):
        """returns block's width."""
        return self.BOARD_WIDTH // COLUMNS

    def draw_board(self):
        """Draw's board's outline."""
        outline = pygame.Surface((self.BOARD_WIDTH + 40, self.BOARD_HEIGHT + 40))
        outline.fill(GREY)
        self.WINDOW.blit(outline, (self.board_pos[0] - 20, self.board_pos[1] - 20))

        board = pygame.Surface((self.BOARD_WIDTH, self.BOARD_HEIGHT))
        board.fill(BLACK)
        self.WINDOW.blit(board, self.board_pos)

        for piece in self.game.board:
            pygame.draw.rect(self.WINDOW, self.game.board[piece],
                             pygame.Rect(piece[0] * self.block_width + self.board_pos[0],
                                         piece[1] * self.block_width + self.board_pos[1],
                                         self.block_width,
                                         self.block_width))

    def draw_piece(self):
        """Draws piece in the position in the screen in the board."""
        split_piece = self.game.piece.piece.split("\n")
        # Splits pieces format row by row.

        for ri, row in zip(range(self.game.piece.pos[1], self.game.piece.pos[1] + len(split_piece)), split_piece):
            for ci, square in zip(range(self.game.piece.pos[0], self.game.piece.pos[0] + len(row)), row):
                # We iterate over both the positions of the squares in the piece
                # Based on it's position and each square,
                # row by row, column by column,

                if square == "#":
                    # If the square is a pound symbol, we draw the square (see pieces.py).
                    pygame.draw.rect(self.WINDOW,
                                     self.game.piece.color,
                                     pygame.Rect(ci * self.block_width + self.board_pos[0],
                                                 ri * self.block_width + self.board_pos[1],
                                                 self.block_width,
                                                 self.block_width))


Window(800, 800, 400)
