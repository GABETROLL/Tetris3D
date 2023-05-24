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
        self.fps = 60
        self.running = True

        self.font = font

        self.level_menu = Menu(range(20))
        self.mode_menu = Menu(("2D", "3D"))
        self.music_menu = Menu(("Tetris Theme", "Silence"))
        self.game_options_menu = Menu((self.level_menu, self.mode_menu, self.music_menu))
        # game options information

        self.controls = GameControl2D(self.window)

        self.frame_handler = self.handle_title_screen_frame
        """
        current "mode" the program is in,
        a method that will be called each frame.
        The methods can be:
        'self.handle_title_screen_frame',
        'self.handle_game_frame',
        'self.handle_game_over_screen_frame'
        """

        while self.running:
            self.clock.tick(self.fps)

            self.window.fill(BLACK)

            self.frame_handler()

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
        stores in 'self', and switches 'self.frame_handler' to
        'self.handle_game_frame' if the player pressed ENTER.
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
                    self.game_options_menu.move_to_next()
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.game_options_menu.move_to_previous()
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.game_options_menu.option.move_to_next()
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.game_options_menu.option.move_to_previous()

                if event.key == pygame.K_RETURN:
                    self.init_game()
                    self.frame_handler = self.handle_game_frame

        self.window.blit(TITLE, (20, 50))

        self.window.blit(STARTING_LEVEL_TEXT, (20, 100))
        CHOSEN_LEVEL_TEXT = CHOSEN_OPTION_FONT.render(str(self.game_options_menu.options[0].option), False, BRIGHT_GREY)
        self.window.blit(CHOSEN_LEVEL_TEXT, (20, 150))

        self.window.blit(GAME_MODE_TEXT, (20, 200))
        CHOSEN_GAME_MODE_TEXT = CHOSEN_OPTION_FONT.render(str(self.game_options_menu.options[1].option), False, BRIGHT_GREY)
        self.window.blit(CHOSEN_GAME_MODE_TEXT, (20, 250))

        self.window.blit(BACKGROUND_MUSIC_TEXT, (20, 300))
        CHOSEN_MUSIC_TEXT = CHOSEN_OPTION_FONT.render(str(self.game_options_menu.options[2].option), False, BRIGHT_GREY)
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

        GAME_CONTINUES = self.controls.play_game_step(key_down_keys)
        if not GAME_CONTINUES:
            self.frame_handler = self.handle_game_over_screen_frame

    def handle_game_over_screen_frame(self):
        """
        Just draws "GAME OVER" on the screen,
        along with two options:
        one to go back to the title screen,
        and one to exit the script.
        """
        FONT_NAME = "consolas"

        GAME_OVER_STR = "GAME OVER"
        GAME_OVER_FONT = pygame.font.SysFont(FONT_NAME, min((self.WIDTH // len(GAME_OVER_STR), self.HEIGHT // 2)))
        # If the letters in "GAME OVER" are roughly squares
        # in the rendered Surface with the word,
        # then you'd expect the font size that fits the window to be
        # 1/9 of the window's width, OR LESS, AND
        # the "GAME OVER" and buttons texts have to fit in 'self.HEIGHT'.
        GAME_OVER_TEXT = GAME_OVER_FONT.render(GAME_OVER_STR, False, BRIGHT_GREY)

        TRY_AGAIN_STR = "Back to title screen"
        # using len(TRY_AGAIN_STR), since it's the longer string.
        OPTION_FONT = pygame.font.SysFont(FONT_NAME, min(self.WIDTH // len(TRY_AGAIN_STR), self.HEIGHT // 4))

        TRY_AGAIN_TEXT = OPTION_FONT.render(TRY_AGAIN_STR, False, BRIGHT_GREY)
        QUIT_TEXT = OPTION_FONT.render("Quit", False, BRIGHT_GREY)

        GAME_OVER_TEXT_POS = (
            (self.WIDTH >> 1) - (GAME_OVER_TEXT.get_width() >> 1),
            (self.HEIGHT >> 1) - (GAME_OVER_FONT.get_height() >> 1)
        )

        self.window.blit(
            GAME_OVER_TEXT,
            GAME_OVER_TEXT_POS
        )

        self.window.blit(
            TRY_AGAIN_TEXT,
            ((GAME_OVER_TEXT_POS[0], GAME_OVER_TEXT_POS[1] + GAME_OVER_TEXT.get_height()))
        )

        self.window.blit(
            QUIT_TEXT,
            ((GAME_OVER_TEXT_POS[0], GAME_OVER_TEXT_POS[1] + GAME_OVER_TEXT.get_height() + TRY_AGAIN_TEXT.get_height()))
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.frame_handler = self.handle_title_screen_frame
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

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
        the vertical slices are drawn BACK-FRONT
        (INCLUDING THE BLOCKS OF THE PIECE AT THAT SLICE)

        TODO: make slices increase in size
        """

        slices = [{} for slice_pos in range(game.game_3d.FLOOR_WIDTH)]
        for block_pos_in_game, block_color in self.controls.game.board.items():
            slices[block_pos_in_game[1]][block_pos_in_game] = block_color
        # Each slice of the board, SUB-DICTIONARIES OF THE BOARD,
        # ordered from front-to-back
        # (we want to iterate through them backwards)

        for block_pos_in_game in self.controls.game.piece.block_positions():
            slices[block_pos_in_game[1]][block_pos_in_game] = self.controls.game.piece.color
        # MAKE SURE TO INCLUDE THE PIECE'S BLOCKS AS WELL!!
        # (In their corresponding slices and positions, and with their corresponding piece color)

        # for each slice in the board (BACK->FRONT)
        # BECAUSE when drawing the ones at the front later,
        # we 'override' the ones at the back,
        # "blocking" their colors and therefore acheiving
        # "perspective"
        for display_darkness, slice in zip(range(len(slices), 0, -1), reversed(slices)):

            for block_pos_in_game, block_color in slice.items():
                BLOCK_POS_IN_SCREEN = (
                    self.board_pos[0] + self.block_width * block_pos_in_game[0],
                    self.board_pos[1] + self.block_width * block_pos_in_game[2]
                )

                block_color = (
                    block_color[0] / display_darkness,
                    block_color[1] / display_darkness,
                    block_color[2] / display_darkness
                )

                pygame.draw.rect(self.window, block_color, pygame.Rect(*BLOCK_POS_IN_SCREEN, self.block_width, self.block_width))

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
