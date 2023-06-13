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

This file also has a Menu class, a very simple class containing
menu options, a choice pointer index and an option property to recieve it.

'Window' has 'handle_game_over_frame' and 'handle_title_screen_frame', which
use the Menu objects with the game mode/level/music options
(kept in 'Window ''self', as well) which render/control the game over and
title screens.

God bless you, enjoy!
"""
import pygame
import game
from game_control import GameControl, GameControl2D, GameControl3D, Z_AXIS
from dataclasses import dataclass
from random import choice as random_choice
from itertools import count

WHITE = (255, 255, 255)
BRIGHT_GREY = (128, 128, 128)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)


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
    BORDER_WIDTH = 20
    """in pixels"""

    def __init__(self, board_height: int, font: pygame.font.Font):
        # We have to make sure the board )and the next piece) can fit in the window.
        # So, we define the window size later
        self.BOARD_HEIGHT = board_height

        self.HEIGHT = board_height
        self.WIDTH = self.HEIGHT

        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True

        self.font = font

        self.COLORED_BORDER_BLOCK_WIDTH = 3
        """
        It's here to make sure that the titles and options
        in the title/game-over screens don't overlap
        with the border, and to center them COMPLETELY INSIDE
        the border.
        """
        self.border_blocks = {}
        """
        (The only reason this is here, is so that
        we can produce the same squares every frame,
        and not have them randomly chosen every frame,
        which can hurt to look at, and could cause seizures)

        Almost like 'self.controls.game.board',
        but for the title/gamover screen's border
        decoration, which should be made of blocks
        of Tetromino colors

        (TODO: MAKE THEM TETROMINOS)
        """
        self._init_border()

        self.level_menu = Menu(range(41))
        self.mode_menu = Menu(("2D", "3D"))
        self.music_menu = Menu(("Tetris Theme", "Silence"))
        self.game_options_menu = Menu((self.level_menu, self.mode_menu, self.music_menu))
        # game options information

        self.controls: GameControl = GameControl2D()

        self.frame_handler = self.handle_title_screen_frame
        """
        current "mode" the program is in,
        a method that will be called each frame.
        The methods can be:
        'self.handle_title_screen_frame',
        'self.handle_game_frame',
        'self.handle_game_over_screen_frame'
        """

        self.game_over_menu =  Menu(("Back to title screen", "Quit"))

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
            self.controls = GameControl2D()
        elif self.mode_menu.option == "3D":
            self.controls = GameControl3D()
        else:
            raise ValueError("Dimension chosen shouldn't be possible!")

        self.controls.game.score_manager.level = self.level_menu.option

    @property
    def block_width_2D(self):
        """
        The width of a 2D block in the game's board,
        'self.BOARD_HEIGHT // game.game_2d.ROWS'
        """
        return self.BOARD_HEIGHT // game.game_2d.ROWS
    
    @property
    def colored_border_pixel_width(self):
        """
        The amount of PIXELS of width OR HEIGHT that the colorful
        borders have.
        """
        return self.block_width_2D * self.COLORED_BORDER_BLOCK_WIDTH

    def _init_border(self):
        """
        Fills 'self.border_blocks' with random-colored blocks, to fulfill
        the promis in its docstring.
        
        Put this code here, since it would be too long to put in the __init__.
        Shouldn't be used for anything more than just the __init__.
        """
        PIECE_COLORS = tuple(
            piece_data[-1]
            for piece_data in (
                game.game_2d.I,
                game.game_2d.J,
                game.game_2d.L,
                game.game_2d.O,
                game.game_2d.S,
                game.game_2d.T,
                game.game_2d.Z
            )
        )

        # draw each side of the border, first the top
        for ri in range(game.game_2d.ROWS):
            for ci in range(self.COLORED_BORDER_BLOCK_WIDTH - 1):
                self.border_blocks[(ri, ci)] = random_choice(PIECE_COLORS)
        for ri in range(self.COLORED_BORDER_BLOCK_WIDTH - 1):
            for ci in range(game.game_2d.ROWS):
                self.border_blocks[(ri, ci)] = random_choice(PIECE_COLORS)
        for ri in range(game.game_2d.ROWS):
            for ci in range(game.game_2d.ROWS - (self.COLORED_BORDER_BLOCK_WIDTH - 1), game.game_2d.ROWS):
                self.border_blocks[(ri, ci)] = random_choice(PIECE_COLORS)
        for ri in range(game.game_2d.ROWS - (self.COLORED_BORDER_BLOCK_WIDTH - 1), game.game_2d.ROWS):
            for ci in range(game.game_2d.ROWS):
                self.border_blocks[(ri, ci)] = random_choice(PIECE_COLORS)

    @staticmethod
    def text_font_fit_to_screen(
        text_str: str,
        width: int,
        height: int,
        font_name: str
    ) -> pygame.font.Font:
        """
        Returns (an estimate of) the biggest font
        that fits the rendered text 'text_str'
        in a surface
        with 'width' width and 'height' height
        """
        # guess font with its size being the window's height
        font_size: int = height
        font = pygame.font.SysFont(font_name, height)

        # test to see if text would fit window
        text_width, text_height = font.size(text_str)

        # shrink font size to fit text to screen, in both x and y
        # (I only claim that this approximates the screen's size)
        if text_width > width:
            font_size = int(font_size * (width / text_width))
        if text_height > height:
            font_size = int(font_size * (height / text_height))

        # re-define font with its size actually fitting screen
        font = pygame.font.SysFont(font_name, font_size)

        return font
    
    def _draw_piece2D(self, piece: game.game_2d.Piece2D, block_width: int, board_pos: tuple[int, int]):
        """
        Draws 2D piece in 'self.window' in its correct position in the board,
        which should be located in the window at 'board_pos', and have its blocks'
        widths AND HEIGHTS be 'block_width.
        """
        for ci, ri in piece.square_positions():
            pygame.draw.rect(
                self.window,
                piece.color,
                pygame.Rect(
                    ci * block_width + board_pos[0],
                    ri * block_width + board_pos[1],
                    block_width,
                    block_width
                )
            )

    def _draw_design_border(self):
        """
        Draws tetrominos as borders inside the screen, as an asthetic design.

        Uses a bunch of hard-coded piece objects and places them on the screen,
        VERYFING that this window's WIDTH and HEIGHT are the same, so that
        the pieces can be written
        AS IF the window was a board
        with dimensions (ROWS x ROWS) INSTEAD OF (COLUNMS x COLUMNS)
        """
        assert self.WIDTH == self.HEIGHT
        assert self.HEIGHT == self.BOARD_HEIGHT

        assert self.window.get_width() == self.WIDTH
        assert self.window.get_height() == self.HEIGHT

        BLOCK_WIDTH = self.BOARD_HEIGHT // game.game_2d.ROWS

        for (ci, ri), color in self.border_blocks.items():
            color = tuple(3 * channel >> 2 for channel in color)
            pygame.draw.rect(
                self.window,
                color,
                pygame.Rect(
                    ci * BLOCK_WIDTH,
                    ri * BLOCK_WIDTH,
                    BLOCK_WIDTH,
                    BLOCK_WIDTH
                )
            )

        # TODO: USE self._draw_piece2D(piece, BLOCK_WIDTH, BORDER_BOARD_POS)

    def handle_title_screen_frame(self):
        """
        Dislays:
        - border in 'self.border_blocks' (in __init__).
        - title centered at the top of the "hole" of the border.
        - level, mode and music selection from the player
        All of these, COMPLETELY INSIDE the border.
        ---
        Keeps track of those selections in 'self.game_options_menu',
        and switches 'self.frame_handler' to
        'self.handle_game_frame' if the player pressed ENTER.

        """
        assert self.WIDTH == self.HEIGHT
        # Make sure the screen is a square, so that all of the tiles fit.

        # DRAWING FIRST, THEN HANDLING MENU INPUTS

        self._draw_design_border()

        WIDTH_INSIDE_BORDER: int = self.WIDTH - 2 * self.colored_border_pixel_width

        TITLE_STR = "Tetris 3D!"
        TITLE_FONT = self.text_font_fit_to_screen(
            TITLE_STR,
            WIDTH_INSIDE_BORDER,
            2 * self.block_width_2D,
            "consolas"
        )
        TITLE = TITLE_FONT.render("Tetris 3D!", False, WHITE)

        ALL_OPTION_STRINGS = sum(
            ([str(option) for option in menu.options] for menu in self.game_options_menu.options),
            start=[]
        )
        SUB_TITLE_STRINGS = "Starting level:", "Game mode:", "Background music:"

        # (except the title string)

        MENU_FONT = self.text_font_fit_to_screen(
            max(
                ALL_MENU_STRINGS := ALL_OPTION_STRINGS + list(SUB_TITLE_STRINGS),
                key=lambda any_menu_str: len(any_menu_str)
            ),
            WIDTH_INSIDE_BORDER,
            self.block_width_2D,
            "consolas"
        )
        # The font for all things in the menu string (except the title)
        # NEEDS to be small enough for the biggest string ("static" text or chosen option)
        # to fit withing one tile of height, and between the borders of the screen
        # (drawn near the top of this function)

        current_text_y_pos: int = self.colored_border_pixel_width
        """
        to blit everything lower and lower in the window
        """

        self.window.blit(
            TITLE,
            (
                (self.WIDTH >> 1) - (TITLE.get_width() >> 1),
                current_text_y_pos
            )
        )

        TEXT_X_POS: int = self.colored_border_pixel_width
        """
        The texts' left sides should be "glued" to the right of the left border
        (except the title, that was just blitted, just above)
        """

        # drawing every text in the screen with 1 tile of space in between
        # (not considering the controls text at the bottom of the screen)
        current_text_y_pos += 3 * self.block_width_2D

        for sub_title, menu in zip(
            SUB_TITLE_STRINGS,
            self.game_options_menu.options,
        ):
            # print(sub_title, menu)
            CHOSEN_OPTION_STR = str(menu.option)

            # draw sub-title
            SUB_TITLE_TEXT = MENU_FONT.render(sub_title, False, WHITE)
            self.window.blit(SUB_TITLE_TEXT, (TEXT_X_POS, current_text_y_pos))

            current_text_y_pos += self.block_width_2D

            # draw chosen menu option
            CHOSEN_OPTION_TEXT = MENU_FONT.render(
                CHOSEN_OPTION_STR,
                False,
                YELLOW if menu is self.game_options_menu.option else WHITE
            )
            self.window.blit(CHOSEN_OPTION_TEXT, (TEXT_X_POS, current_text_y_pos))

            current_text_y_pos += 2 * self.block_width_2D
        
        CONTROLS_STRINGS = (
            "W/S: scroll through menu",
            "A/D: change option ENTER: play",
            "Controls: "
        )

        CONTROLS_FONT = self.text_font_fit_to_screen(
            max(CONTROLS_STRINGS, key=lambda s: len(s)),
            WIDTH_INSIDE_BORDER,
            self.block_width_2D,
            "Consolas"
        )

        BORDER_BOTTOM: int = self.HEIGHT - self.colored_border_pixel_width

        current_text_y_pos: int = BORDER_BOTTOM
        """
        Now we're using it to blit the controls texts
        from the bottom-border-up
        """

        for control_str in reversed(CONTROLS_STRINGS):
            CONTROL_TEXT = CONTROLS_FONT.render(control_str, False, WHITE)

            current_text_y_pos -= CONTROL_TEXT.get_height()

            self.window.blit(
                CONTROL_TEXT, (TEXT_X_POS, current_text_y_pos)
            )

        # DRAWING DONE, HANDLING MENU INPUTS

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
        Draws asthetic border in 'self.border_blocks',
        "GAME OVER" on the screen,
        along with two options:
        one to go back to the title screen,
        and one to exit the script.

        These options are stored in 'self.game_over_menu',
        to handle every frame.

        To scroll:
        w/UP or s/DOWN
        To select: ENTER
        """
        self._draw_design_border()

        FONT_NAME = "consolas"

        assert self.WIDTH == self.HEIGHT

        WIDTH_INSIDE_BORDER = self.WIDTH - 2 * self.colored_border_pixel_width

        GAME_OVER_STR = "GAME OVER"
        GAME_OVER_FONT = self.text_font_fit_to_screen(
            GAME_OVER_STR,
            WIDTH_INSIDE_BORDER,
            3 * self.block_width_2D,
            FONT_NAME
        )
        # If the letters in "GAME OVER" are roughly squares
        # in the rendered Surface with the word,
        # then you'd expect the font size that fits the window to be
        # 1/9 of the window's width, OR LESS, AND
        # the "GAME OVER" and buttons texts have to fit in 'self.HEIGHT'.

        GAME_OVER_TEXT = GAME_OVER_FONT.render(GAME_OVER_STR, False, WHITE)

        TEXT_POS = [
            (self.WIDTH >> 1) - (GAME_OVER_TEXT.get_width() >> 1),
            self.colored_border_pixel_width
        ]
        # should be "moved" vertically,
        # to make sure the texts don't overlap

        self.window.blit(GAME_OVER_TEXT, TEXT_POS)
        TEXT_POS[1] += 3 * self.block_width_2D
        # "GAME OVER" should occupy 3 tiles vertically,
        # and we want the score to be directly under the "GAME OVER",
        # so the new text pos should be 3 tiles below.

        SCORE_STR = f"Score: {self.controls.game.score_manager.points}"
        SCORE_FONT = self.text_font_fit_to_screen(SCORE_STR, GAME_OVER_TEXT.get_width(), GAME_OVER_TEXT.get_height(), FONT_NAME)
        SCORE_TEXT = SCORE_FONT.render(SCORE_STR, False, WHITE)

        TEXT_POS[0] = (self.WIDTH >> 1) - (SCORE_TEXT.get_width() >> 1)
        self.window.blit(SCORE_TEXT, TEXT_POS)

        TEXT_POS[1] += 4 * self.block_width_2D
        # we want the options to be one tile of distance from the score text

        OPTION_FONT = self.text_font_fit_to_screen(
            max(self.game_over_menu.options, key=lambda option: len(str(option))),
            # To make sure both menu options fit the screen's width,
            # the longest option string is the one we must try to fit in 'WIDTH_INSIDE_BORDER'.
            WIDTH_INSIDE_BORDER,
            self.block_width_2D,
            FONT_NAME
        )

        for option in self.game_over_menu.options:
            OPTION_TEXT = OPTION_FONT.render(
                option,
                False,
                YELLOW if option == self.game_over_menu.option else WHITE
            )
            self.window.blit(OPTION_TEXT, TEXT_POS)
            TEXT_POS[1] += self.block_width_2D

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                # move around menu
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.game_over_menu.move_to_next()
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.game_over_menu.move_to_previous()

                # submit menu selection
                if event.key == pygame.K_RETURN:
                    if self.game_over_menu.option == "Quit":
                        self.running = False
                        # quit
                    else:  # elif menu.option == "Back to title screen"
                        self.frame_handler = self.handle_title_screen_frame

        CONTROLS_STR = "W/S: scroll through menu ENTER: choose option"
        CONTROLS_FONT = self.text_font_fit_to_screen(
            CONTROLS_STR,
            WIDTH_INSIDE_BORDER,
            self.block_width_2D,
            FONT_NAME
        )
        CONTROLS_TITLE = CONTROLS_FONT.render("Controls: ", False, WHITE)
        CONTROLS_TEXT = CONTROLS_FONT.render(CONTROLS_STR, False, WHITE)

        BOTTOM_INSIDE_BORDER: int = self.HEIGHT - self.colored_border_pixel_width
        TEXT_POS = [self.colored_border_pixel_width, BOTTOM_INSIDE_BORDER - CONTROLS_TEXT.get_height()]

        self.window.blit(CONTROLS_TEXT, TEXT_POS)

        TEXT_POS[1] += CONTROLS_TITLE.get_height()

        self.window.blit(CONTROLS_TITLE, TEXT_POS)

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

        
        BOARD_WIDTH = int(self.BOARD_HEIGHT * (game.game_2d.COLUMNS / game.game_2d.ROWS))
        BLOCK_WIDTH = BOARD_WIDTH // game.game_2d.COLUMNS
        BOARD_POS = self.WIDTH // 2 - BOARD_WIDTH // 2, self.HEIGHT // 2 - self.BOARD_HEIGHT // 2
        # to draw board

        # DRAW BOARD:

        # board outline
        NEXT_PIECE_OUTLINE = pygame.Surface((BOARD_WIDTH + (Window.BORDER_WIDTH << 1), self.BOARD_HEIGHT + (Window.BORDER_WIDTH << 1)))
        NEXT_PIECE_OUTLINE.fill(BRIGHT_GREY)
        self.window.blit(NEXT_PIECE_OUTLINE, (BOARD_POS[0] - Window.BORDER_WIDTH, BOARD_POS[1] - Window.BORDER_WIDTH))

        # board background
        board = pygame.Surface((BOARD_WIDTH, self.BOARD_HEIGHT))
        board.fill(BLACK)
        self.window.blit(board, BOARD_POS)

        # board blocks
        for piece in self.controls.game.board:
            pygame.draw.rect(self.window, self.controls.game.board[piece],
                             pygame.Rect(piece[0] * BLOCK_WIDTH + BOARD_POS[0],
                                         piece[1] * BLOCK_WIDTH + BOARD_POS[1],
                                         BLOCK_WIDTH,
                                         BLOCK_WIDTH))
    
        # draw piece
        self._draw_piece2D(self.controls.game.piece, BLOCK_WIDTH, BOARD_POS)

        # draw next piece in its own little box beside the board
        NEXT_PIECE: game.game_2d.Piece = self.controls.game.next_piece

        NEXT_PIECE_BOX_HEIGHT = NEXT_PIECE.piece_height * BLOCK_WIDTH
        NEXT_PIECE_BOX_WIDTH = NEXT_PIECE.piece_height * BLOCK_WIDTH

        # Its outline will be overlayed on the board's outline.
        BOARD_RIGHT = BOARD_POS[0] + BOARD_WIDTH

        NEXT_PIECE_OUTLINE = pygame.Surface((
            NEXT_PIECE_BOX_WIDTH + (Window.BORDER_WIDTH << 1),
            NEXT_PIECE_BOX_HEIGHT + (Window.BORDER_WIDTH << 1)
        ))
        NEXT_PIECE_OUTLINE.fill(BRIGHT_GREY)
        NEXT_PIECE_OUTLINE_POS = (
            BOARD_RIGHT,
            BOARD_POS[1] + (self.BOARD_HEIGHT >> 1) - (NEXT_PIECE_OUTLINE.get_height() >> 1),
        )

        # The plan here is to make a "next piece box" surface,
        # display the 'NEXT_PIECE' here,
        # then blit this surface into the main window.
        next_piece_box = pygame.Surface((NEXT_PIECE_BOX_WIDTH, NEXT_PIECE_BOX_HEIGHT))
        next_piece_box.fill(BLACK)

        next_piece_square_surface = pygame.Surface((BLOCK_WIDTH, BLOCK_WIDTH))
        next_piece_square_surface.fill(NEXT_PIECE.color)

        for square_position in self.controls.game.next_piece.relative_square_positions():
            SQUARE_POSITION_IN_BOX = square_position[0] * BLOCK_WIDTH, square_position[1] * BLOCK_WIDTH
            next_piece_box.blit(next_piece_square_surface, SQUARE_POSITION_IN_BOX)
        
        NEXT_PIECE_BOX_POS = (
            BOARD_RIGHT + Window.BORDER_WIDTH,
            BOARD_POS[1] + (self.BOARD_HEIGHT >> 1) - (next_piece_box.get_height() >> 1)
        )
        
        NEXT_PIECE_TEXT = self.font.render("Next", False, WHITE)

        # Next box rendering complete, now it's time to blit the next box.
        self.window.blit(
            NEXT_PIECE_OUTLINE,
            NEXT_PIECE_OUTLINE_POS
        )
        self.window.blit(
            next_piece_box,
            NEXT_PIECE_BOX_POS
        )
        self.window.blit(
            NEXT_PIECE_TEXT,
            (
                NEXT_PIECE_BOX_POS[0],
                NEXT_PIECE_OUTLINE_POS[1] + NEXT_PIECE_OUTLINE.get_height()
            )
        )

        CONTROLS_STRINGS = (
            "A/D: move piece LEFT/RIGHT",
            "S/LEFT SHIFT: SOFT-DROP",
            "SPACEBAR: HARD-DROP",
            "U: rotate counter-clockwise",
            "O: rotate clockwise"
        )

        CONTROLS_FONT = self.text_font_fit_to_screen(
            max(CONTROLS_STRINGS, key=lambda s: len(s)),
            BOARD_POS[0],
            self.HEIGHT,
            "consolas"
        )

        blit_pos = [0, self.HEIGHT]

        for controls_string in reversed(CONTROLS_STRINGS):
            CONTROLS_TEXT = CONTROLS_FONT.render(
                controls_string, False, WHITE
            )

            blit_pos[1] -= CONTROLS_TEXT.get_height()

            self.window.blit(
                CONTROLS_TEXT,
                blit_pos
            )

    def draw_3d(self):
        """
        Draws the 'self.game_control.game' board, piece
        and next piece, AFTER drawing a grid backgound
        for easier gameplay,
        IF THE GAME MODE IS 3D.

        IF 'self.game_control' is 2D, a TypeError
        will be raised.

        The grid is drawn at the left, right, back and bottom of the board.

        The method for drawing the pieces is simple:
        the vertical slices are drawn BACK-FRONT
        (INCLUDING THE BLOCKS OF THE PIECE AT THAT SLICE)
        And the slices get bigger and bigger, brighter and brighter,
        as if they were getting closer to the camera.

        The slices are drawn FIRST by drawing each of the slices' block's
        backs and sides, then each of the blocks' front sides,
        in order to avoid wrong overlapping order, since the front side is supposed
        to be on top of every other side by default, and since
        drawing a plygon into the pygame window overrides any other pixels there.

        The slice's tops should all be aligned, as if the camera were
        looking from the very top, in order to help the player
        know where the pieces land.

        The next piece is drawn as if it were in the board, beside the board,
        at a certain amount of blocks away from it.
        (For now I've chosen 1 block of distance)
        """

        if self.mode_menu.option != "3D":
            raise TypeError("Game mode is 2D, but 'draw_3d' was called!")

        slices = [{} for slice_pos in range(game.game_3d.FLOOR_WIDTH)]
        """
        Each FRONT-FACING SLICE of the board, AS IF IT INCLUDED THE PIECE'S BLOCKS,
        as dictionaries of 3D positions and colors.

        It also contains the game's next piece's blocks, as if the piece were
        floating beside the board, in order to draw the next piece in 3D,
        without needing to repeat much code.
        """
        # add board blocks to 'slices'
        for block_pos_in_game, block_color in self.controls.game.board.items():
            slices[block_pos_in_game[1]][block_pos_in_game] = block_color
        # add piece blocks 'slices'
        for block_pos_in_game in self.controls.game.piece.block_positions():
            slices[block_pos_in_game[1]][block_pos_in_game] = self.controls.game.piece.color
        # add next_piece blocks to 'slices'
        NEXT_PIECE_DISPLAY_POSITION = (
            5,
            (game.game_3d.FLOOR_WIDTH >> 1) - (self.controls.game.next_piece.blocks.shape[1] >> 1),
            (game.game_3d.FLOORS >> 1) - (self.controls.game.next_piece.blocks.shape[2] >> 1)
        )
        OLD_NEXT_PIECE_POS = self.controls.game.next_piece.pos
        # temporarily change the next piece's pos to store its block positions
        # (I CHANGE IT BACK AT THE BOTTOM OF THIS FUNCTION)
        self.controls.game.next_piece.pos = NEXT_PIECE_DISPLAY_POSITION
        # store the next piece's block positions
        for block_pos_in_game in self.controls.game.next_piece.block_positions():
            slices[block_pos_in_game[1]][block_pos_in_game] = self.controls.game.next_piece.color

        FRONT_SLICE_FRONT_WIDTH = int(self.BOARD_HEIGHT * (game.game_3d.FLOOR_WIDTH / game.game_3d.FLOORS))
        DISTANCE_TO_FRONT_SLICE_FRONT = max((game.game_3d.FLOOR_WIDTH, game.game_3d.FLOORS))
        """
        Arbitrary value, meant to represent the imagined distance
        from the "camera" to front of the board,
        A.K.A, the front side of the cubes in the front side of the board.
        """
        DISTANCE_TO_BACK_SLICE_BACK = DISTANCE_TO_FRONT_SLICE_FRONT + len(slices) - 1

        SLICES_LATTICE_POINTS_IN_SCREEN = []
        """
        All of the positions
        of all of the lattice points
        of all of the slices of the board.
        AKA:
        SLICES_LATTICE_POINTS_IN_SCREEN[y_in_game] -> slice lattice points
        SLICES_LATTICE_POINTS_IN_SCREEN[y_in_game][x_in_game] -> slice lattice point (row? column?)
        SLICES_LATTICE_POINTS_IN_SCREEN[y_in_game][x_in_game][z_in_game] -> slice lattice point

        The points are the (x_in_screen, y_in_screen) pixel positions of the slices' lattice points,
        projected by perspective.
        """
        # SLICES_LATTICE_POINTS_IN_SCREEN[y, x, z] = slice's (aka y) lattice point (aka (x, y)) in screen

        for y_pos_in_game in range(game.game_3d.FLOOR_WIDTH + 1):
            DISTANCE_TO_SLICE = DISTANCE_TO_FRONT_SLICE_FRONT + y_pos_in_game

            PERSPECTIVE_FACTOR = DISTANCE_TO_FRONT_SLICE_FRONT / DISTANCE_TO_SLICE
            # every front-facing square's side-length APPEARS 1 / distance
            # of the square from the camera, if the distance is measured
            # by the side-length of the square.

            # We want the imaginary distance of the front-most slice
            # to be MAX_SLICE_SIDE >> 1 from the camera, to achive a BALANCE
            # between super-warped perspective, and very flat perspective.

            # BUT, since we need the front-most slice to remain our pre-determined
            # size, we need to multiply the factor by 'MAX_SLICE_SIDE'.
            SLICE_FRONT_WIDTH_IN_SCREEN = int(FRONT_SLICE_FRONT_WIDTH * PERSPECTIVE_FACTOR)
            BLOCK_FRONT_WIDTH_IN_SCREEN = SLICE_FRONT_WIDTH_IN_SCREEN // game.game_3d.FLOOR_WIDTH
            # since 'SLICE_FRONT_WIDTH_IN_SCREEN' is the slice's width IN THE SCREEN,
            # and the slice's width is just the sum of all of the block's widths in the slice,
            # which is 'game.game_3d.FLOOR_WIDTH',
            # the slice's front and back display size are these.
            SLICE_POS_IN_SCREEN = self.WIDTH // 2 - SLICE_FRONT_WIDTH_IN_SCREEN // 2, 0
            # positions of the slice's BACKS, IN SCREEN,
            # aligned in the slices' and screen's center in the X axis,
            # aligned at the top for the Y axis for easier perspective in the gameplay.

            SLICES_LATTICE_POINTS_IN_SCREEN.append(
                list(
                    list(
                    (
                        SLICE_POS_IN_SCREEN[0] + BLOCK_FRONT_WIDTH_IN_SCREEN * block_x_pos,
                        SLICE_POS_IN_SCREEN[1] + BLOCK_FRONT_WIDTH_IN_SCREEN * block_z_pos
                    )
                    for block_z_pos in range(game.game_3d.FLOORS + 1)
                )
                for block_x_pos in range(game.game_3d.FLOOR_WIDTH + 1)
                )
            )

        # We must draw the background mesh
        # (BEFORE we draw the board/piece blocks),
        # to help the player see better.

        # draw back side vertical grid lines
        for x_pos in range(game.game_3d.FLOOR_WIDTH + 1):
            pygame.draw.line(
                self.window,
                BRIGHT_GREY,
                SLICES_LATTICE_POINTS_IN_SCREEN[game.game_3d.FLOOR_WIDTH][x_pos][0],
                SLICES_LATTICE_POINTS_IN_SCREEN[game.game_3d.FLOOR_WIDTH][x_pos][game.game_3d.FLOORS]
            )
        # draw back side horizontal grid lines
        for z_pos in range(game.game_3d.FLOORS + 1):
            pygame.draw.line(
                self.window,
                BRIGHT_GREY,
                SLICES_LATTICE_POINTS_IN_SCREEN[game.game_3d.FLOOR_WIDTH][0][z_pos],
                SLICES_LATTICE_POINTS_IN_SCREEN[game.game_3d.FLOOR_WIDTH][game.game_3d.FLOOR_WIDTH][z_pos]
            )
        
        # draw sides' vertical grid lines
        for y_pos in range(game.game_3d.FLOOR_WIDTH):
            # left
            pygame.draw.line(
                self.window,
                BRIGHT_GREY,
                SLICES_LATTICE_POINTS_IN_SCREEN[y_pos][0][0],
                SLICES_LATTICE_POINTS_IN_SCREEN[y_pos][0][game.game_3d.FLOORS]
            )
            # right
            pygame.draw.line(
                self.window,
                BRIGHT_GREY,
                SLICES_LATTICE_POINTS_IN_SCREEN[y_pos][game.game_3d.FLOOR_WIDTH][0],
                SLICES_LATTICE_POINTS_IN_SCREEN[y_pos][game.game_3d.FLOOR_WIDTH][game.game_3d.FLOORS]
            )
        # draw sides' horizontal grid lines
        for z_pos in range(game.game_3d.FLOORS):
            # left
            pygame.draw.line(
                self.window,
                BRIGHT_GREY,
                SLICES_LATTICE_POINTS_IN_SCREEN[0][0][z_pos],
                SLICES_LATTICE_POINTS_IN_SCREEN[game.game_3d.FLOOR_WIDTH][0][z_pos]
            )
            # right
            pygame.draw.line(
                self.window,
                BRIGHT_GREY,
                SLICES_LATTICE_POINTS_IN_SCREEN[0][game.game_3d.FLOOR_WIDTH][z_pos],
                SLICES_LATTICE_POINTS_IN_SCREEN[game.game_3d.FLOOR_WIDTH][game.game_3d.FLOOR_WIDTH][z_pos]
            )
        
        # draw floor's horizontal grid lines
        for x_pos in range(game.game_3d.FLOOR_WIDTH):
            pygame.draw.line(
                self.window,
                BRIGHT_GREY,
                SLICES_LATTICE_POINTS_IN_SCREEN[0][x_pos][game.game_3d.FLOORS],
                SLICES_LATTICE_POINTS_IN_SCREEN[game.game_3d.FLOOR_WIDTH][x_pos][game.game_3d.FLOORS]
            )
        # draw floor's "vertical" grid lines
        for y_pos in range(game.game_3d.FLOOR_WIDTH):
            pygame.draw.line(
                self.window,
                BRIGHT_GREY,
                SLICES_LATTICE_POINTS_IN_SCREEN[y_pos][0][game.game_3d.FLOORS],
                SLICES_LATTICE_POINTS_IN_SCREEN[y_pos][game.game_3d.FLOOR_WIDTH][game.game_3d.FLOORS]
            )

        # IMPORTANT: IF THE GAME LAGS, YOU COULD JUST USE THE LATTICE POINTS STORED IN
        # 'SLICES_LATTICE_POINTS' CONSTANT, IN THIS METHOD SCOPE,
        # TO AVOID HAVING TO CALCULATE ALL OF THE BLOCK POLYGON PIXEL POSITIONS!

        # for each slice in the board (BACK->FRONT),
        # because drawing a rectangle on the screen
        # just overrides whatever was there,
        # We achieve blocks at the front "blocking"
        # the view from the ones behind.
        for distance_to_slice_front, slice \
            in zip(
                range(DISTANCE_TO_BACK_SLICE_BACK, DISTANCE_TO_FRONT_SLICE_FRONT - 1, -1),
                reversed(slices)
        ):
            distance_to_slice_back = distance_to_slice_front + 1
            BACK_PERSPECTIVE_FACTOR = DISTANCE_TO_FRONT_SLICE_FRONT / distance_to_slice_back
            
            FRONT_PERSPECTIVE_FACTOR = DISTANCE_TO_FRONT_SLICE_FRONT / distance_to_slice_front
            # (again with this one)

            SLICE_BACK_WIDTH_IN_SCREEN = int(FRONT_SLICE_FRONT_WIDTH * BACK_PERSPECTIVE_FACTOR)
            BLOCK_BACK_WIDTH_IN_SCREEN = SLICE_BACK_WIDTH_IN_SCREEN // game.game_3d.FLOOR_WIDTH
           
            SLICE_FRONT_WIDTH_IN_SCREEN = int(FRONT_SLICE_FRONT_WIDTH * FRONT_PERSPECTIVE_FACTOR)
            BLOCK_FRONT_WIDTH_IN_SCREEN = SLICE_FRONT_WIDTH_IN_SCREEN // game.game_3d.FLOOR_WIDTH
            # (again with this one)

            SLICE_BACK_POS_IN_SCREEN = self.WIDTH // 2 - SLICE_BACK_WIDTH_IN_SCREEN // 2, 0
            SLICE_FRONT_POS_IN_SCREEN = self.WIDTH // 2 - SLICE_FRONT_WIDTH_IN_SCREEN // 2, 0
            # positions of the slice's fronts and backs IN THE SCREEN,
            # aligned in the slices' and screen's center in the X axis,
            # aligned at the top for the Y axis for easier perspective in the gameplay.

            # DRAWING 3 FACES BEHIND CUBE
            # (the lower face doesn't need to be drawn,
            # SINCE THE SLICES ARE ALIGNED AT THE TOP, VERTICALLY,
            # and therefore won't be visible to the player)

            BRIGHTNESS_DISTANCE = DISTANCE_TO_FRONT_SLICE_FRONT >> 2
            BRIGHTNESS_FACTOR = BRIGHTNESS_DISTANCE ** 2 / (distance_to_slice_front - DISTANCE_TO_FRONT_SLICE_FRONT + BRIGHTNESS_DISTANCE) ** 2

            for block_pos_in_game, block_color in slice.items():

                block_color = tuple(
                    rgb_brightness * BRIGHTNESS_FACTOR
                    for rgb_brightness in block_color
                )
                # block color is meant to simulate how much light should get to the camera,
                # from the block at a given distance:
                # just as how a square with side-lengths S that's N units away from a camera
                # appears to have sides of length S / N, the amount of light recieved from a
                # square that's N units away from a camera should reflect 1 / N of the light
                # that's recieved from a square one unit away.

                TOP_LEFT_BACK_BLOCK_CORNER_POS = (
                    SLICE_BACK_POS_IN_SCREEN[0] + BLOCK_BACK_WIDTH_IN_SCREEN * block_pos_in_game[0],
                    SLICE_BACK_POS_IN_SCREEN[1] + BLOCK_BACK_WIDTH_IN_SCREEN * block_pos_in_game[2]
                )
                TOP_RIGHT_BACK_BLOCK_CORNER_POS = (
                    TOP_LEFT_BACK_BLOCK_CORNER_POS[0] + BLOCK_BACK_WIDTH_IN_SCREEN,
                    TOP_LEFT_BACK_BLOCK_CORNER_POS[1]
                )
                BOTTOM_LEFT_BACK_BLOCK_CORNER_POS = (
                    TOP_LEFT_BACK_BLOCK_CORNER_POS[0],
                    TOP_LEFT_BACK_BLOCK_CORNER_POS[1] + BLOCK_BACK_WIDTH_IN_SCREEN 
                )
                BOTTOM_RIGHT_BACK_BLOCK_CORNER_POS = (
                    BOTTOM_LEFT_BACK_BLOCK_CORNER_POS[0] + BLOCK_BACK_WIDTH_IN_SCREEN,
                    BOTTOM_LEFT_BACK_BLOCK_CORNER_POS[1]
                )

                TOP_LEFT_FRONT_BLOCK_CORNER_POS = (
                    SLICE_FRONT_POS_IN_SCREEN[0] + BLOCK_FRONT_WIDTH_IN_SCREEN * block_pos_in_game[0],
                    SLICE_FRONT_POS_IN_SCREEN[1] + BLOCK_FRONT_WIDTH_IN_SCREEN * block_pos_in_game[2]
                )
                TOP_RIGHT_FRONT_BLOCK_CORNER_POS = (
                    TOP_LEFT_FRONT_BLOCK_CORNER_POS[0] + BLOCK_FRONT_WIDTH_IN_SCREEN,
                    TOP_LEFT_FRONT_BLOCK_CORNER_POS[1]
                )
                BOTTOM_LEFT_FRONT_BLOCK_CORNER_POS = (
                    TOP_LEFT_FRONT_BLOCK_CORNER_POS[0],
                    TOP_LEFT_FRONT_BLOCK_CORNER_POS[1] + BLOCK_FRONT_WIDTH_IN_SCREEN 
                )
                BOTTOM_RIGHT_FRONT_BLOCK_CORNER_POS = (
                    BOTTOM_LEFT_FRONT_BLOCK_CORNER_POS[0] + BLOCK_FRONT_WIDTH_IN_SCREEN,
                    BOTTOM_LEFT_FRONT_BLOCK_CORNER_POS[1]
                )

                # If we don't draw sides clockwise/counter-clockwise order
                # each side's 4 corners, polygons may not come out right!
                # DRAW TOP SIDE OF CUBE
                pygame.draw.polygon(
                    self.window,
                    block_color,
                    (
                        TOP_LEFT_BACK_BLOCK_CORNER_POS, TOP_RIGHT_BACK_BLOCK_CORNER_POS,
                        TOP_RIGHT_FRONT_BLOCK_CORNER_POS, TOP_LEFT_FRONT_BLOCK_CORNER_POS
                    )
                )
                # DRAW LEFT SIDE OF CUBE
                pygame.draw.polygon(
                    self.window,
                    block_color,
                    (
                       TOP_LEFT_BACK_BLOCK_CORNER_POS, TOP_LEFT_FRONT_BLOCK_CORNER_POS,
                       BOTTOM_LEFT_FRONT_BLOCK_CORNER_POS, BOTTOM_LEFT_BACK_BLOCK_CORNER_POS 
                    )
                )
                # DRAW RIGHT SIDE OF CUBE
                pygame.draw.polygon(
                    self.window,
                    block_color,
                    (
                        TOP_RIGHT_FRONT_BLOCK_CORNER_POS, TOP_RIGHT_BACK_BLOCK_CORNER_POS,
                        BOTTOM_RIGHT_BACK_BLOCK_CORNER_POS, BOTTOM_RIGHT_FRONT_BLOCK_CORNER_POS
                    )
                )

            for block_pos_in_game, block_color in slice.items():

                block_color = tuple(
                    rgb_brightness * BRIGHTNESS_FACTOR
                    for rgb_brightness in block_color
                )
                # block color is meant to simulate how much light should get to the camera,
                # from the block at a given distance:
                # just as how a square with side-lengths S that's N units away from a camera
                # appears to have sides of length S / N, the amount of light recieved from a
                # square that's N units away from a camera should reflect 1 / N of the light
                # that's recieved from a square one unit away.

                TOP_LEFT_FRONT_BLOCK_CORNER_POS = (
                    SLICE_FRONT_POS_IN_SCREEN[0] + BLOCK_FRONT_WIDTH_IN_SCREEN * block_pos_in_game[0],
                    SLICE_FRONT_POS_IN_SCREEN[1] + BLOCK_FRONT_WIDTH_IN_SCREEN * block_pos_in_game[2]
                )
                TOP_RIGHT_FRONT_BLOCK_CORNER_POS = (
                    TOP_LEFT_FRONT_BLOCK_CORNER_POS[0] + BLOCK_FRONT_WIDTH_IN_SCREEN,
                    TOP_LEFT_FRONT_BLOCK_CORNER_POS[1]
                )
                BOTTOM_LEFT_FRONT_BLOCK_CORNER_POS = (
                    TOP_LEFT_FRONT_BLOCK_CORNER_POS[0],
                    TOP_LEFT_FRONT_BLOCK_CORNER_POS[1] + BLOCK_FRONT_WIDTH_IN_SCREEN 
                )
                BOTTOM_RIGHT_FRONT_BLOCK_CORNER_POS = (
                    BOTTOM_LEFT_FRONT_BLOCK_CORNER_POS[0] + BLOCK_FRONT_WIDTH_IN_SCREEN,
                    BOTTOM_LEFT_FRONT_BLOCK_CORNER_POS[1]
                )

                # DRAW FRONT SIDE OF CUBE
                pygame.draw.polygon(
                    self.window,
                    block_color,
                    (
                        TOP_LEFT_FRONT_BLOCK_CORNER_POS, TOP_RIGHT_FRONT_BLOCK_CORNER_POS,
                        BOTTOM_RIGHT_FRONT_BLOCK_CORNER_POS, BOTTOM_LEFT_FRONT_BLOCK_CORNER_POS
                    )
                )

        # Draw "next" text
        NEXT_PIECE_TEXT = self.font.render("Next", False, WHITE)
        # The text's bottom should be higher than the next piece's highest block,
        # if that block were in the front-most slice of the board

        NEXT_PIECE_TEXT_POS = (
            SLICES_LATTICE_POINTS_IN_SCREEN[0][game.game_3d.FLOOR_WIDTH][0][0],
            # text's left pos is just the right of the board
            # IF BOARD IS TOO WIDE, THE TEXT MAY NOT FIT IN THE WINDOW!
            SLICES_LATTICE_POINTS_IN_SCREEN[0][0][
                max(
                    block_pos[Z_AXIS]
                    for block_pos in self.controls.game.next_piece.block_positions()
                )
            ][1]
        )
        # HERE we change the next piece's pos back to normal.
        self.controls.game.next_piece.pos = OLD_NEXT_PIECE_POS

        # print(SLICES_LATTICE_POINTS_IN_SCREEN)
        # print(NEXT_PIECE_TEXT_POS)

        self.window.blit(NEXT_PIECE_TEXT, NEXT_PIECE_TEXT_POS)

    def draw_score(self):
        """Draws score and level text at the top of the board."""
        white = WHITE
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
