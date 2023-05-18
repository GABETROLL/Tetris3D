"""
Main program file
Has a 'Window' class that renders the game using a pygame window,
and manages the title screen frames and game frames,
and game inputs using pygame.

The game is stored in the GameControl instances (2D/3D),
which control keyoard inputs for the game and the speed
at which the pieces fall.
It is meant to be an extension of the Window class,
but makes this file too long to put in here.

God bless you, enjoy!
"""
import pygame
import game
from game_control import GameControl2D, GameControl3D
from dataclasses import dataclass

BRIGHT_GREY = (128, 128, 128)
BLACK = (0, 0, 0)

RAINBOW = [(255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255)]


@dataclass
class Menu:
    options: object
    option_index: int = 0

    @property
    def option(self):
        return self.options[self.option_index]

    def move_to_next(self):
        self.option_index += 1
        self.option_index %= len(self.options)

    def move_to_previous(self):
        if self.option_index == 0:
            self.option_index = len(self.options) - 1
        else:
            self.option_index -= 1


class Window:
    def __init__(self, board_height: int, font: pygame.font.Font):
        # We have to make sure the board )and the next piece) can fit in the window.
        # So, we define the window size later
        self.BOARD_HEIGHT = board_height
        self.BOARD_WIDTH = int(self.BOARD_HEIGHT * (game.game_2d.COLUMNS / game.game_2d.ROWS))

        self.HEIGHT = board_height
        self.WIDTH = self.HEIGHT

        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.running = True

        self.font = font

        self.fps = 60
        self.controls = GameControl2D(self.window)

        self.playing = False

        self.level_menu = Menu(range(20))
        self.mode_menu = Menu(("2D", "3D"))
        self.music_menu = Menu(("Tetris Theme", "Silence"))

        self.menu_menu = Menu((self.level_menu, self.mode_menu, self.music_menu))

        while self.running:
            self.clock.tick(self.fps)

            self.window.fill(BLACK)

            if self.playing:
                self.handle_game_frame()
            else:
                self.handle_title_screen_frame()

            pygame.display.update()
        pygame.quit()

    def init_game(self):
        """
        Initializes 'self.controls' with the appropiate
        game level to start in.
        """
        if self.mode_menu.option == "2D":
            self.controls = GameControl2D(self.window)
        elif self.mode_menu.option == "3D":
            self.controls = GameControl3D(self.window)
        else:
            raise ValueError("Dimension chosen shouldn't be possible!")

        self.controls.game.score_manager.level = self.level_menu.option

    def handle_title_screen_frame(self):
        """
        Displays and gets level, mode and music selection from the player,
        stores in 'self', and switches 'self.playing' if the player
        pressed ENTER.
        """
        TITLE_FONT = pygame.font.SysFont("consolas", 50)
        TITLE = TITLE_FONT.render("Tetris 3D!", False, BRIGHT_GREY)

        MENU_FONT = pygame.font.SysFont("consolas", 20)
        CHOSEN_OPTION_FONT = pygame.font.SysFont("consolas", 30)

        STARTING_LEVEL_TEXT = MENU_FONT.render("Starting level:", False, BRIGHT_GREY)
        GAME_MODE_TEXT = MENU_FONT.render("Game mode:", False, BRIGHT_GREY)
        BACKGROUND_MUSIC_TEXT = MENU_FONT.render("Background music:", False, BRIGHT_GREY)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.menu_menu.move_to_next()
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.menu_menu.move_to_previous()
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.menu_menu.option.move_to_next()
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.menu_menu.option.move_to_previous()

                if event.key == pygame.K_RETURN:
                    self.init_game()
                    self.playing = True

        self.window.blit(TITLE, (20, 50))

        self.window.blit(STARTING_LEVEL_TEXT, (20, 100))
        CHOSEN_LEVEL_TEXT = CHOSEN_OPTION_FONT.render(str(self.menu_menu.options[0].option), False, BRIGHT_GREY)
        self.window.blit(CHOSEN_LEVEL_TEXT, (20, 150))

        self.window.blit(GAME_MODE_TEXT, (20, 200))
        CHOSEN_GAME_MODE_TEXT = CHOSEN_OPTION_FONT.render(str(self.menu_menu.options[1].option), False, BRIGHT_GREY)
        self.window.blit(CHOSEN_GAME_MODE_TEXT, (20, 250))

        self.window.blit(BACKGROUND_MUSIC_TEXT, (20, 300))
        CHOSEN_MUSIC_TEXT = CHOSEN_OPTION_FONT.render(str(self.menu_menu.options[2].option), False, BRIGHT_GREY)
        self.window.blit(CHOSEN_MUSIC_TEXT, (20, 350))

    def handle_game_frame(self):
        """
        Controls Tetris game.
        """
        key_down_keys = set()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                key_down_keys.add(event.key)
            # Certain keys can't spam an instruction every frame.

        if self.mode_menu.option == "3D":
            self.draw_3d()
        else:
            self.draw_2d()
        self.draw_score()

        self.controls.main(key_down_keys)

    @property
    def board_pos(self):
        """returns (x_pos, y_pos) of the board."""
        return self.WIDTH // 2 - self.BOARD_WIDTH // 2, self.HEIGHT // 2 - self.BOARD_HEIGHT // 2

    @property
    def block_width(self):
        """returns block's width."""
        return self.BOARD_WIDTH // game.game_2d.COLUMNS
    
    def draw_2d(self):
        """
        Draws the 'self.game_control.game' board, piece
        and next piece, IF THE GAME MODE IS 2D
        
        IF 'self.game_control' is 3D, a TypeError
        will be raised.

        The board is drawn in the middle of the screen.
        The piece is drawn in the correct position INSIDE
        the board.
        The next piece is drawn in a little box beside the board
        """
        if type(self.controls) != GameControl2D:
            raise TypeError("Can't render in 2D while game mode is not 2D!")

        # draw board
        # board outline
        outline = pygame.Surface((self.BOARD_WIDTH + 40, self.BOARD_HEIGHT + 40))
        outline.fill(BRIGHT_GREY)
        self.window.blit(outline, (self.board_pos[0] - 20, self.board_pos[1] - 20))

        # board background
        board = pygame.Surface((self.BOARD_WIDTH, self.BOARD_HEIGHT))
        board.fill(BLACK)
        self.window.blit(board, self.board_pos)

        # board blocks
        for piece in self.controls.game.board:
            pygame.draw.rect(self.window, self.controls.game.board[piece],
                             pygame.Rect(piece[0] * self.block_width + self.board_pos[0],
                                         piece[1] * self.block_width + self.board_pos[1],
                                         self.block_width,
                                         self.block_width))
    
        # draw piece
        for ri, row in zip(range(self.controls.game.piece.pos[1],
                                 self.controls.game.piece.pos[1] + len(self.controls.game.piece.piece)),
                           self.controls.game.piece.piece):
            for ci, square in zip(range(self.controls.game.piece.pos[0],  self.controls.game.piece.pos[0] + len(row)),
                                  row):
                # We iterate over both the positions of the squares in the piece
                # Based on its position and each square,
                # row by row, column by column,

                if square == "#":
                    # If the square is a pound symbol, we draw the square (see pieces.py).
                    pygame.draw.rect(self.window,
                                     self.controls.game.piece.color,
                                     pygame.Rect(ci * self.block_width + self.board_pos[0],
                                                 ri * self.block_width + self.board_pos[1],
                                                 self.block_width,
                                                 self.block_width))

        # draw next piece in its own little box beside the board
        NEXT_PIECE: game.game_2d.Piece = self.controls.game.next_piece

        NEXT_PIECE_BOX_HEIGHT = NEXT_PIECE.piece_height * self.block_width
        NEXT_PIECE_BOX_WIDTH = NEXT_PIECE.piece_height * self.block_width

        outline = pygame.Surface((NEXT_PIECE_BOX_WIDTH + 40, NEXT_PIECE_BOX_HEIGHT + 40))
        outline.fill(BRIGHT_GREY)

        # The plan here is to make a "next piece box" surface,
        # display the 'NEXT_PIECE' here,
        # then blit this surface into the main window.
        next_piece_box = pygame.Surface((NEXT_PIECE_BOX_WIDTH, NEXT_PIECE_BOX_HEIGHT))
        next_piece_box.fill(BLACK)

        next_piece_square_surface = pygame.Surface((self.block_width, self.block_width))
        next_piece_square_surface.fill(NEXT_PIECE.color)

        for square_position in self.controls.game.next_piece.relative_square_positions():
            SQUARE_POSITION_IN_BOX = square_position[0] * self.block_width, square_position[1] * self.block_width
            next_piece_box.blit(next_piece_square_surface, SQUARE_POSITION_IN_BOX)

        # Next box rendering complete, now it's time to blit the next box.
        self.window.blit(next_piece_box, (self.board_pos[0] + self.BOARD_WIDTH, self.board_pos[1] + self.BOARD_HEIGHT // 2))
        # The box is blit half-way down the right side of the board,
        # with 0 pixels of gap between the two.
    
    def draw_3d(self):
        """
        Draws the 'self.game_control.game' board, piece
        and next piece, IF THE GAME MODE IS 3D

        IF 'self.game_control' is 2D, a TypeError
        will be raised.

        The method for drawing the pieces is simple:
        the floors are drawn flat on the screen (no perspective),
        BOTTOM->UP, while the size of the floor on the screen
        keeps increasing, to give perspective.
        """
        for floor_size, floor in zip(
            range(self.block_width * game.game_3d.FLOOR_WIDTH),
            reversed(self.controls.game.floors())
        ):
            FLOOR_POS = self.WIDTH // 2 - floor_size // 2, self.HEIGHT - floor_size // 2
            FLOOR_TILE_WIDTH = floor_size // game.game_3d.FLOOR_WIDTH

            for block_pos_in_game, block_color in floor.items():
                BLOCK_POS_IN_SCREEN = (
                    FLOOR_POS[0] + FLOOR_TILE_WIDTH * block_pos_in_game[0],
                    FLOOR_POS[1] + FLOOR_TILE_WIDTH * block_pos_in_game[1]
                )
                pygame.draw.rect(self.window, block_color, pygame.Rect(*BLOCK_POS_IN_SCREEN, (FLOOR_TILE_WIDTH, FLOOR_TILE_WIDTH)))

    def draw_score(self):
        """Draws score and level text at the top of the board."""
        white = (255, 255, 255)
        text = self.font.render(f"Score: {self.controls.game.score_manager.points}, "
                                f"Level: {self.controls.game.score_manager.level}, "
                                f"Lines: {self.controls.game.score_manager.lines}",
                                True,
                                white)
        position = self.WIDTH // 2 - text.get_width() // 2, 10
        self.window.blit(text, position)


if __name__ == "__main__":
    pygame.init()
    Window(800, pygame.font.SysFont("consolas", 30))
