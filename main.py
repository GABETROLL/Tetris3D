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
from game_control import GameControl, GameControl2D, GameControl3D, Z_AXIS, \
    controls_keys, CONTROL_KEYS_FILE
from dataclasses import dataclass
from random import choice as random_choice
from collections.abc import Sequence
from itertools import count
from json import dump as dump_as_json
import sound

WHITE = (255, 255, 255)
BRIGHT_GREY = (128, 128, 128)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BUTTON_COLOR = (0, 0, 0xC0)


@dataclass
class Menu:
    options: Sequence[object]
    option_index: int = 0
    title: str = ""

    @property
    def option(self):
        return self.options[self.option_index]
    
    @option.setter
    def option(self, value):
        if value not in self.options:
            raise ValueError(f"option={value} must be inside menu={self}!")
        self.option_index = self.options.index()

    def move_to_next(self):
        self.option_index += 1
        self.option_index %= len(self.options)

    def move_to_previous(self):
        if self.option_index == 0:
            self.option_index = len(self.options) - 1
        else:
            self.option_index -= 1


class Window:
    GREY_BORDER_WIDTH = 20
    """
    For the 2D board,
    measured in pixels.
    """

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

        self.controls: GameControl = None

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

    def start_game(self):
        """
        Initializes 'self.controls' with the appropiate
        game level to start in,

        and assigns 'self.frame_handler' to 'self.handle_game_frame'
        to start the game screen's loop.
        """
        if self.mode_menu.option == "2D":
            self.controls = GameControl2D()
        elif self.mode_menu.option == "3D":
            self.controls = GameControl3D()
        else:
            raise ValueError("Dimension chosen shouldn't be possible!")

        self.controls.game.score_manager.level = self.level_menu.option

        self.frame_handler = self.handle_game_frame

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

    def _handle_controls_screen_button(
            self,
            button_rect: pygame.Rect
        ) -> bool:
        """
        Renders "Controls" button in 'consolas' font,
        with 'BUTTON_COLOR' background and 'WHITE' background,

        and RETURNS weather or not being HOVERED
        """
        CONTROLS_STR = "Controls"
        CONTROLS_FONT = self.text_font_fit_to_screen(
            CONTROLS_STR,
            button_rect.width,
            button_rect.height,
            "consolas"
        )
        pygame.draw.rect(self.window, BUTTON_COLOR, button_rect)
        self.window.blit(
            CONTROLS_FONT.render(CONTROLS_STR, False, WHITE),
            (button_rect.topleft)
        )

        return button_rect.collidepoint(pygame.mouse.get_pos())

    @property
    def key_controls_names(self) -> dict:
        """
        Returns the 'controls_keys' dict, but with the key's names.
        """
        return {
            action: [pygame.key.name(key) for key in keys]
            for action, keys in controls_keys.items()
        }

    def controls_screen_loop(self):
        """
        Displays all keyboard inputs and what they do, described in
        'CONTROL_KEYS_FILE'.

        If the user clicks on a control, it's selected, and it displays
        "Press any key...". When the user presses a key that isn't
        'controls_keys["toggle_controls_screen"]', the new key is set as the
        action's key, in 'controls_keys'.

        When the player presses 'controls_keys["toggle_controls_screen"]'
        while there isn't a selected control, this method THE CONTROLS
        ('controls_keys') in 'controls_keys_FILE',
        and exits the loop, and returns None.
        "
        """

        CLICKED_ACTION: str = None

        while self.running:
            STARTED_CLICKING_THIS_FRAME: bool = False
            MOUSE_POS: tuple[int, int] = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key in controls_keys["toggle_controls_screen"]:
                        return

                    if CLICKED_ACTION is not None:
                        if event.key not in controls_keys["toggle_controls_screen"]:
                            controls_keys[CLICKED_ACTION] = [event.key]

                        CLICKED_ACTION = None

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    STARTED_CLICKING_THIS_FRAME = True

            assert type(controls_keys) == dict
            assert type(self.key_controls_names) == dict

            self.window.fill(BLACK)

            self._draw_design_border()

            WIDTH_INSIDE_BORDER = self.WIDTH - (self.colored_border_pixel_width << 1)

            CONTROLS_FONT_HEIGHT = self.block_width_2D
            CONTROLS_FONT = self.text_font_fit_to_screen(
                max(
                    list(self.key_controls_names.keys()) + list(self.key_controls_names.values()),
                    key=lambda control_string: len(control_string)
                ),
                WIDTH_INSIDE_BORDER >> 1,
                # each control row looks like this:
                # action: key
                # We want to have them at the left...
                # ...and right halves of the screen.
                CONTROLS_FONT_HEIGHT,
                "consolas"
            )

            for blit_y_pos, (action, action_keys) in zip(
                count(self.colored_border_pixel_width, CONTROLS_FONT_HEIGHT),
                controls_keys.items()
            ):
                TEXT_COLOR = WHITE

                if self.colored_border_pixel_width < MOUSE_POS[0] < self.WIDTH - self.colored_border_pixel_width \
                        and blit_y_pos < MOUSE_POS[1] < blit_y_pos + CONTROLS_FONT_HEIGHT:
                    TEXT_COLOR = YELLOW

                    if STARTED_CLICKING_THIS_FRAME:
                        CLICKED_ACTION = action

                        sound.SFX_CHANNEL.play(sound.SUBMITED_IN_MENU)

                if action == CLICKED_ACTION:
                    TEXT_COLOR = YELLOW

                LEFT_COLUMN_X_POS = self.colored_border_pixel_width
                # aka the LEFT EDGE of the LEFT HALF inside the border
                RIGHT_COLUMN_X_POS = self.colored_border_pixel_width + (WIDTH_INSIDE_BORDER >> 1)
                # aka the LEFT EDGE of the RIGHT HALF inside the border

                ACTION_TEXT = CONTROLS_FONT.render(action, False, TEXT_COLOR)

                ACTION_KEYS_NAMES = (pygame.key.name(key) for key in action_keys)
                ACTION_KEYS_STR = f": {' | '.join(ACTION_KEYS_NAMES)}"

                KEYS_TEXT = CONTROLS_FONT.render(
                    "Press any key..." if action == CLICKED_ACTION else ACTION_KEYS_STR,
                    False,
                    TEXT_COLOR
                )

                self.window.blit(ACTION_TEXT, (LEFT_COLUMN_X_POS, blit_y_pos))

                self.window.blit(KEYS_TEXT, (RIGHT_COLUMN_X_POS, blit_y_pos))

            pygame.display.update()

        dump_as_json(open(CONTROL_KEYS_FILE), self.key_controls_names)

    def handle_title_screen_frame(self):
        """
        Dislays:
        - border in 'self.border_blocks' (in __init__).
        - title centered at the top of the "hole" of the border.
        - level, mode and music selections (menus) menu, with < and > arrows
        - to scroll through the options in each sub-menu

        All of these, COMPLETELY INSIDE the border.

        "Scrolls" to different option if user clicks < or > arrows,
        or uses WASD to move around the options and sub-menus.

        assigns 'self.handle_game_frame' to 'self.frame_handler' if user clicks
        "Play!" button or presses ENTER key.
        """
        assert self.WIDTH == self.HEIGHT
        # Make sure the screen is a square, so that all of the tiles fit.

        # DRAW TITLE AND BORDER, THEN HANDLE & DRAW MENU AT THE SAME TIME:
        self._draw_design_border()

        WIDTH_INSIDE_BORDER: int = self.WIDTH - 2 * self.colored_border_pixel_width

        TITLE_Y_POS: int = self.colored_border_pixel_width
        """
        to blit everything lower and lower in the window
        """

        # Drawing title:
        TITLE_STR = "Tetris 3D!"
        TITLE_FONT = self.text_font_fit_to_screen(
            TITLE_STR,
            WIDTH_INSIDE_BORDER,
            2 * self.block_width_2D,
            "consolas"
        )
        TITLE = TITLE_FONT.render("Tetris 3D!", False, WHITE)

        self.window.blit(
            TITLE,
            (
                (self.WIDTH >> 1) - (TITLE.get_width() >> 1),
                TITLE_Y_POS
            )
        )

        # HANDLE & DISPLAY MENU:

        # All of this is just for displaying the menu,
        # preparing fonts for tile sizes and text box dimensions
        # present in the menu's dimensions:
        MENU_TOP_Y_POS = TITLE_Y_POS + 3 * self.block_width_2D
        """
        TO: draw every text in the screen
        right below eachother, sub-title text or chosen option text.

        ALL of the texts will be rendered right below eachother,
        and ALL OF THEM will have ONE TILE OF HEIGHT.
        """
        y_blit_pos = MENU_TOP_Y_POS
        """
        TO: draw every text in the screen
        right below eachother, sub-title text or chosen option text.

        ALL of the texts will be rendered right below eachother,
        and ALL OF THEM will have ONE TILE OF HEIGHT.
        """

        # PREPARE FONT for menu sub-titles and chosen options, with their < > arrows
        ALL_POSSIBLE_OPTION_STRINGS = sum(
            ([str(option) for option in menu.options] for menu in self.game_options_menu.options),
            start=[]
        )
        SUB_TITLE_STRINGS = "Starting level:", "Game mode:", "Background music:"
        # (except the title string)

        MENU_FONT = self.text_font_fit_to_screen(
            max(
                ALL_MENU_STRINGS := ALL_POSSIBLE_OPTION_STRINGS + list(SUB_TITLE_STRINGS),
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

        LEFT_INSIDE_BORDER: int = self.colored_border_pixel_width
        """
        The texts' left sides should be "glued" to the right of the left border
        (except the title, that was just blitted, just above)
        """

        MOUSE_POS = pygame.mouse.get_pos()

        # Font done, now HAMDLING KEYBOARD inputs,
        # and STORING MOUSE INPUTS for later,
        # to be handled using the same positions
        # being used to render the menu options:

        STARTED_CLICKING_THIS_FRAME: bool = False
        """
        Weather or not the user just pressed the mouse button THIS FRAME,
        AND NOT THE PREVIOUS FRAME.
        """
        SCROLLING_UP: bool = False
        """
        Weather or not the user is CURRENTLY scrolling "up" the options
        (which are sideways, but they should scroll LEFT)
        """
        SCROLLING_DOWN: bool = False
        """
        Weather or not the user is CURRENTLY scrolling "down" the options
        (which are sideways, but they should scroll RIGHT)
        """

        STARTED_CLICKING_THIS_FRAME: bool = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                STARTED_CLICKING_THIS_FRAME = True

            SCROLLING_UP = event.type == pygame.MOUSEWHEEL and event.y < 0
            SCROLLING_DOWN = event.type == pygame.MOUSEWHEEL and event.y > 0

            if event.type == pygame.KEYDOWN:
                # ENTER controls screen, UNTIL user decides to exit it.
                if event.key in controls_keys["toggle_controls_screen"]:
                    self.controls_screen_loop()

                # scroll through sub-menus/menu options WITH KEYBOARD
                if event.key in controls_keys["DOWN"]:
                    self.game_options_menu.move_to_next()
                if event.key in controls_keys["UP"]:
                    self.game_options_menu.move_to_previous()
                if event.key in controls_keys["RIGHT"]:
                    self.game_options_menu.option.move_to_next()
                if event.key in controls_keys["LEFT"]:
                    self.game_options_menu.option.move_to_previous()

                # press "Play!" button" or its key
                if event.key in controls_keys["menu_submit"]:
                    self.start_game()
                    # game should start IMMEDIATELY if the button is pressed,
                    # without altering options last-frame
                    sound.SFX_CHANNEL.play(sound.SUBMITED_IN_MENU)
                    break

            # only cares about THIS frame's inputs,
            # REGARDLESS of the buttons being off/on the previous frame.
            # (NO pygame.events USED HERE, LOOK UP)
            if SCROLLING_UP:
                self.game_options_menu.option.move_to_next()
            elif SCROLLING_DOWN:
                self.game_options_menu.option.move_to_previous()
            
            if SCROLLING_UP or SCROLLING_DOWN:
                sound.SFX_CHANNEL.play(sound.SCROLLING_OVER_MENU_OPTION)

        if self._handle_controls_screen_button(
            pygame.Rect(
                (self.COLORED_BORDER_BLOCK_WIDTH - 1) * self.block_width_2D,
                (self.COLORED_BORDER_BLOCK_WIDTH - 1) * self.block_width_2D,
                4 * self.block_width_2D,
                1 * self.block_width_2D
            )
        ) and STARTED_CLICKING_THIS_FRAME:
            self.controls_screen_loop()

        # RENDER MENU:

        for index, (sub_title, menu) in enumerate(
            zip(
                SUB_TITLE_STRINGS,
                self.game_options_menu.options,
            )
        ):
            # render sub-title text (below previous chosen option text)
            SUB_TITLE_TEXT = MENU_FONT.render(sub_title, False, WHITE)
            self.window.blit(SUB_TITLE_TEXT, (LEFT_INSIDE_BORDER, y_blit_pos))

            y_blit_pos += self.block_width_2D

            # COMPUTE POSITIONS for < > arrows and option text
            # AND RENDER option text

            OPTION_COLOR = YELLOW if menu is self.game_options_menu.option else WHITE
            # depending on if the option is selected or not

            LEFT_ARROW_RECT = pygame.Rect(LEFT_INSIDE_BORDER, y_blit_pos, self.block_width_2D, self.block_width_2D)

            CHOSEN_OPTION_STR = str(menu.option)
            CHOSEN_OPTION_TEXT = MENU_FONT.render(
                CHOSEN_OPTION_STR,
                False,
                OPTION_COLOR
            )
            CHOSEN_OPTION_RECT = CHOSEN_OPTION_TEXT.get_rect()
            CHOSEN_OPTION_RECT.topleft = (LEFT_ARROW_RECT.right, y_blit_pos)

            RIGHT_ARROW_RECT = LEFT_ARROW_RECT.copy()
            RIGHT_ARROW_RECT.x = CHOSEN_OPTION_RECT.right

            # RENDER < > arrows and BLIT option text
            pygame.draw.polygon(self.window, OPTION_COLOR, (LEFT_ARROW_RECT.midleft, LEFT_ARROW_RECT.topright, LEFT_ARROW_RECT.bottomright))
            self.window.blit(CHOSEN_OPTION_TEXT, CHOSEN_OPTION_RECT.topleft)
            pygame.draw.polygon(self.window, OPTION_COLOR, (RIGHT_ARROW_RECT.bottomleft, RIGHT_ARROW_RECT.topleft, RIGHT_ARROW_RECT.midright))

            # Hovering over the options and their arrows, automatically highlighting them,
            # as if the user were scrolling through them with W/S,
            # would be quite nice!
            if LEFT_ARROW_RECT.collidepoint(*MOUSE_POS) \
                    or CHOSEN_OPTION_RECT.collidepoint(*MOUSE_POS) \
                    or RIGHT_ARROW_RECT.collidepoint(*MOUSE_POS):
                if self.game_options_menu.option_index != index:
                    # ...BUT WE ONLY NEED to PLAY THE SCROLLING SFX and change the menu option
                    # IF we currenty don't have this option,
                    # the option with index 'index', as selected.
                    self.game_options_menu.option_index = index

                    sound.SFX_CHANNEL.play(sound.SCROLLING_OVER_MENU_OPTION)

            y_blit_pos += self.block_width_2D

            # HANDLE ARROW INPUTS:

            # checks if user clicked IN each arrow individually
            if STARTED_CLICKING_THIS_FRAME:
                if LEFT_ARROW_RECT.collidepoint(*MOUSE_POS):
                    menu.move_to_previous()

                    sound.SFX_CHANNEL.play(sound.SCROLLING_OVER_MENU_OPTION)
                elif RIGHT_ARROW_RECT.collidepoint(*MOUSE_POS):
                    menu.move_to_next()

                    sound.SFX_CHANNEL.play(sound.SCROLLING_OVER_MENU_OPTION)

        # RENDER "Play!" BUTTON:

        y_blit_pos += self.block_width_2D

        PLAY_BUTTON = MENU_FONT.render("Play!", False, WHITE, BUTTON_COLOR)
        PLAY_BUTTON_POS = ((self.WIDTH >> 1) - (PLAY_BUTTON.get_width() >> 1), y_blit_pos)
        self.window.blit(PLAY_BUTTON, PLAY_BUTTON_POS)

        # HANDLE CLICK IN "Play!" BUTTON:
        PLAY_RECT = PLAY_BUTTON.get_rect()
        PLAY_RECT.topleft = PLAY_BUTTON_POS

        if STARTED_CLICKING_THIS_FRAME and PLAY_RECT.collidepoint(*MOUSE_POS):
            self.start_game()
            sound.SFX_CHANNEL.play(sound.SUBMITED_IN_MENU)
        # game should start IMMEDIATELY if the button is pressed,
        # without altering options last-frame.
        # Right now, that's already being achieved.

        # Draw controls strings: (last thing to do here)
        CONTROLS_STRINGS = (
            "Controls:",
            f"{'/'.join(self.key_controls_names['UP'])}/{'/'.join(self.key_controls_names['DOWN'])}: move down",
            f"{'/'.join(self.key_controls_names['LEFT'])}/{'/'.join(self.key_controls_names['RIGHT'])}: change option",
            f"{'/'.join(self.key_controls_names['menu_submit'])}: play",
        )

        CONTROLS_FONT = self.text_font_fit_to_screen(
            max(CONTROLS_STRINGS, key=lambda s: len(s)),
            WIDTH_INSIDE_BORDER,
            self.block_width_2D >> 1,
            "Consolas"
        )

        BORDER_BOTTOM: int = self.HEIGHT - self.colored_border_pixel_width

        TITLE_Y_POS: int = BORDER_BOTTOM
        """
        Now we're using it to blit the controls texts
        from the bottom-border-up
        """

        for control_str in reversed(CONTROLS_STRINGS):
            CONTROL_TEXT = CONTROLS_FONT.render(control_str, False, WHITE)

            self.window.blit(
                CONTROL_TEXT, (LEFT_INSIDE_BORDER, TITLE_Y_POS)
            )

            TITLE_Y_POS -= CONTROL_TEXT.get_height()

    def handle_game_frame(self):
        """
        Controls Tetris game.
        """
        key_down_keys = set()

        STARTED_CLICKING_THIS_FRAME: bool = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                key_down_keys.add(event.key)
            # Certain keys can't spam an instruction every frame.

            if event.type == pygame.MOUSEBUTTONDOWN:
                STARTED_CLICKING_THIS_FRAME = True
            # neither should the controls button click

        STARTED_CLICKING_CONTROLS_BUTTON: bool = self._handle_controls_screen_button(
            pygame.Rect(0, 0, 4 * self.block_width_2D, 1 * self.block_width_2D)
        ) and STARTED_CLICKING_THIS_FRAME

        if any(
            toggle_controls_screen_key in key_down_keys
            for toggle_controls_screen_key in controls_keys["toggle_controls_screen"]
        ) or STARTED_CLICKING_CONTROLS_BUTTON:
            self.controls_screen_loop()

        if self.mode_menu.option == "3D":
            self.draw_3d()
        else:
            self.draw_2d()
        self.draw_score()

        GAME_CONTINUES = self.controls.play_game_step(key_down_keys)

        if self.controls.game.amount_of_levels_cleared:
            sound.SFX_CHANNEL.play(sound.CLEARED_BLOCKS)
            self.controls.game.amount_of_levels_cleared = 0

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

        text_pos = [
            (self.WIDTH >> 1) - (GAME_OVER_TEXT.get_width() >> 1),
            self.colored_border_pixel_width
        ]
        # should be "moved" vertically,
        # to make sure the texts don't overlap

        self.window.blit(GAME_OVER_TEXT, text_pos)
        text_pos[1] += 3 * self.block_width_2D
        # "GAME OVER" should occupy 3 tiles vertically,
        # and we want the score to be directly under the "GAME OVER",
        # so the new text pos should be 3 tiles below.

        SCORE_STR = f"Score: {self.controls.game.score_manager.points}"
        SCORE_FONT = self.text_font_fit_to_screen(SCORE_STR, GAME_OVER_TEXT.get_width(), GAME_OVER_TEXT.get_height(), FONT_NAME)
        SCORE_TEXT = SCORE_FONT.render(SCORE_STR, False, WHITE)

        text_pos[0] = (self.WIDTH >> 1) - (SCORE_TEXT.get_width() >> 1)
        self.window.blit(SCORE_TEXT, text_pos)

        text_pos[1] += 4 * self.block_width_2D
        # we want the options to be one tile of distance from the score text

        MOUSE_POS: tuple[int, int] = pygame.mouse.get_pos()
        # We need to have the mouse's position THIS FRAME,
        # to click the menu options.

        OPTION_FONT = self.text_font_fit_to_screen(
            max(self.game_over_menu.options, key=lambda option: len(str(option))),
            # To make sure both menu options fit the screen's width,
            # the longest option string is the one we must try to fit in 'WIDTH_INSIDE_BORDER'.
            WIDTH_INSIDE_BORDER,
            self.block_width_2D,
            FONT_NAME
        )

        mouse_hovered_option_index: int = None

        for option_index, option_rect in enumerate(self.game_over_menu.options):
            OPTION_TEXT = OPTION_FONT.render(
                option_rect,
                False,
                YELLOW if option_rect == self.game_over_menu.option else WHITE
            )
            OPTION_TEXT_RECT: pygame.Rect = OPTION_TEXT.get_rect()
            OPTION_TEXT_RECT.x, OPTION_TEXT_RECT.y = text_pos

            # We want to automatically SCROLL TO the option the mouse
            # is hovering over, if it is hovering one,
            # and play the scrolling SFX if it is.
            if OPTION_TEXT_RECT.collidepoint(*MOUSE_POS):

                mouse_hovered_option_index = option_index
                # If the mouse clicked in this frame, we want to
                # submit that option, which will be done later,
                # but we need to keep track of it, here.

                # We also don't want it to ONLY activate when the mouse
                # JUST has arrived at this option, since that would
                # make the first available option un-clickable
                # unless the player starts scrolling through them first!

                if self.game_over_menu.option_index != option_index:
                    # ...But we don't want to re-choose the option
                    # if we're already there, so that the sound effect
                    # doesn't play every frame.

                    self.game_over_menu.option_index = option_index

                    sound.SFX_CHANNEL.play(sound.SCROLLING_OVER_MENU_OPTION)

            self.window.blit(OPTION_TEXT, text_pos)

            text_pos[1] += self.block_width_2D
        
        STARTED_CLICKING_THIS_FRAME: bool = False

        for event in pygame.event.get():
            # user presses X button of window
            # (or red buton in Mac)
            if event.type == pygame.QUIT:
                self.running = False
            
            option_chosen: bool = False

            if event.type == pygame.KEYDOWN:
                # Enter controls screen
                if event.key in controls_keys["toggle_controls_screen"]:
                    self.controls_screen_loop()
                # move around menu
                if event.key in controls_keys["DOWN"]:
                    self.game_over_menu.move_to_next()
                if event.key in controls_keys["UP"]:
                    self.game_over_menu.move_to_previous()

                # submit menu selection
                if event.key in controls_keys["menu_submit"]:
                    option_chosen = True
                    sound.SFX_CHANNEL.play(sound.SUBMITED_IN_MENU)

            if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                STARTED_CLICKING_THIS_FRAME = True

                # HANDLE CLICK, CHOOSE OPTION IF (left)-CLICKED USER CLICKED AN OPTION
                # (we know if the user clicked one, and which one the clicked,
                # if 'mouse_hovered_option_index' is not None.)
                if mouse_hovered_option_index is not None:
                    self.game_over_menu.option_index = mouse_hovered_option_index
                    option_chosen = True
                    sound.SFX_CHANNEL.play(sound.SUBMITED_IN_MENU)

            # HANDLE SELECTED OPTION
            if option_chosen:
                if self.game_over_menu.option == "Quit":
                    self.running = False
                    # quit
                else:  # elif menu.option == "Back to title screen"
                    self.frame_handler = self.handle_title_screen_frame
        
        STARTED_CLICKING_CONTROLS_BUTTON: bool = self._handle_controls_screen_button(
            pygame.Rect(
                (self.COLORED_BORDER_BLOCK_WIDTH - 1) * self.block_width_2D,
                (self.COLORED_BORDER_BLOCK_WIDTH - 1) * self.block_width_2D,
                4 * self.block_width_2D,
                1 * self.block_width_2D)
        ) and STARTED_CLICKING_THIS_FRAME

        if STARTED_CLICKING_CONTROLS_BUTTON:
            self.controls_screen_loop()

        CONTROLS_STRINGS = (
            "Controls:",
            f"{'/'.join(self.key_controls_names['UP'] + self.key_controls_names['DOWN'])}: scroll through menu",
            f"{'/'.join(self.key_controls_names['menu_submit'])}: choose option"
        )
        CONTROLS_FONT = self.text_font_fit_to_screen(
            max(CONTROLS_STRINGS, key=lambda control_string: len(control_string)),
            WIDTH_INSIDE_BORDER,
            self.block_width_2D,
            FONT_NAME
        )

        BOTTOM_INSIDE_BORDER: int = self.HEIGHT - self.colored_border_pixel_width
        text_pos = [self.colored_border_pixel_width, BOTTOM_INSIDE_BORDER]

        for control_string in reversed(CONTROLS_STRINGS):
            CONTROL_TEXT = CONTROLS_FONT.render(control_string, False, WHITE)

            text_pos[1] -= CONTROL_TEXT.get_height()

            self.window.blit(CONTROL_TEXT, text_pos)

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
        NEXT_PIECE_OUTLINE = pygame.Surface((BOARD_WIDTH + (Window.GREY_BORDER_WIDTH << 1), self.BOARD_HEIGHT + (Window.GREY_BORDER_WIDTH << 1)))
        NEXT_PIECE_OUTLINE.fill(BRIGHT_GREY)
        self.window.blit(NEXT_PIECE_OUTLINE, (BOARD_POS[0] - Window.GREY_BORDER_WIDTH, BOARD_POS[1] - Window.GREY_BORDER_WIDTH))

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
            NEXT_PIECE_BOX_WIDTH + (Window.GREY_BORDER_WIDTH << 1),
            NEXT_PIECE_BOX_HEIGHT + (Window.GREY_BORDER_WIDTH << 1)
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
            BOARD_RIGHT + Window.GREY_BORDER_WIDTH,
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
            "LEFT:",
            f"{'/'.join(self.key_controls_names['LEFT'])}",
            "RIGHT:",
            f"{'/'.join(self.key_controls_names['RIGHT'])}",
            "SOFT_DROP:",
            f"{'/'.join(self.key_controls_names['SOFT_DROP'])}",
            "HARD-DROP:",
            f"{'/'.join(self.key_controls_names['HARD_DROP'])}",
            "ROTATE CCW:",
            f"{'/'.join(self.key_controls_names['rotate_ccw_y'])}",
            "ROTATE CW:",
            f"{'/'.join(self.key_controls_names['rotate_cw_y'])}"
        )

        CONTROLS_FONT = self.text_font_fit_to_screen(
            max(CONTROLS_STRINGS, key=lambda s: len(s)),
            BOARD_POS[0] - Window.GREY_BORDER_WIDTH,
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

        CONTROLS_STRINGS = (
            "Controls:"
            f"LEFT : {'/'.join(self.key_controls_names['LEFT'])}",
            f"RIGHT : {'/'.join(self.key_controls_names['RIGHT'])}",
            f"BACK: {'/'.join(self.key_controls_names['UP'])}",
            f"FRONT: {'/'.join(self.key_controls_names['DOWN'])}",
            f"SOFT-DROP: {'/'.join(self.key_controls_names['SOFT_DROP'])}",
            f"HARD_DROP: {'/'.join(self.key_controls_names['HARD_DROP'])}",
        ) + sum(
            (
                (
                    f"Rotate around {axis_name}:"
                    f"CW: {'/'.join(self.key_controls_names[f'rotate_cw_{axis_name}'])}",
                    f"CCW: {'/'.join(self.key_controls_names[f'rotate_ccw_{axis_name}'])}"
                )
                for axis_name in "xyz"
            ),
            start=()
        )

        CONTROLS_FONT = self.text_font_fit_to_screen(
            max(CONTROLS_STRINGS, key=lambda s: len(s)),
            (self.WIDTH - FRONT_SLICE_FRONT_WIDTH) >> 1,
            self.block_width_2D,
            "consolas"
        )

        control_text_y_pos = self.HEIGHT

        for control_str in reversed(CONTROLS_STRINGS):
            CONTROL_TEXT = CONTROLS_FONT.render(control_str, False, WHITE)

            control_text_y_pos -= CONTROL_TEXT.get_height()

            self.window.blit(CONTROL_TEXT, (0, control_text_y_pos))

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
    Window(800, pygame.font.SysFont("consolas", 30))
