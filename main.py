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

        self.fps = 10

        self.game = Board()

        while self.running:
            self.clock.tick(self.fps)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.WINDOW.fill(BLACK)

            self.draw_board()
            self.draw_piece()

            self.game.play()

            pygame.display.update()

        pygame.quit()

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
