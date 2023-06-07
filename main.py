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
from game_control import GameControl2D, GameControl3D
from dataclasses import dataclass
from itertools import chain
from numpy import linspace

BRIGHT_GREY = (128, 128, 128)
BLACK = (0, 0, 0)
YELLOW = (128, 128, 0)

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
        CHOSEN_LEVEL_TEXT = CHOSEN_OPTION_FONT.render(
            str(self.level_menu.option),
            False,
            YELLOW if self.game_options_menu.option is self.level_menu else BRIGHT_GREY
        )
        self.window.blit(CHOSEN_LEVEL_TEXT, (20, 150))

        self.window.blit(GAME_MODE_TEXT, (20, 200))
        CHOSEN_GAME_MODE_TEXT = CHOSEN_OPTION_FONT.render(
            str(self.mode_menu.option),
            False,
            YELLOW if self.game_options_menu.option is self.mode_menu else BRIGHT_GREY
        )
        self.window.blit(CHOSEN_GAME_MODE_TEXT, (20, 250))

        self.window.blit(BACKGROUND_MUSIC_TEXT, (20, 300))
        CHOSEN_MUSIC_TEXT = CHOSEN_OPTION_FONT.render(
            str(self.music_menu.option),
            False,
            YELLOW if self.game_options_menu.option is self.music_menu else BRIGHT_GREY
        )
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

        These options are stored in 'self.game_over_menu',
        to handle every frame.

        To scroll:
        w/UP or s/DOWN
        To select: ENTER
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

        TEXT_POS = [
            (self.WIDTH >> 1) - (GAME_OVER_TEXT.get_width() >> 1),
            (self.HEIGHT >> 1) - (GAME_OVER_TEXT.get_height() >> 1)
        ]

        self.window.blit(GAME_OVER_TEXT, TEXT_POS)
        TEXT_POS[1] += GAME_OVER_TEXT.get_height()

        MAX_OPTION_STR_LEN = max(len(option) for option in self.game_over_menu.options)
        # to make sure both menu options fit the screen's width
        # the 'self.HEIGHT // 4' is to ensure that "GAME OVER" and these menu options
        # fit vertically ("GAME OVER" being double the height of the option text rectangles)
        OPTION_FONT = pygame.font.SysFont(FONT_NAME, min(self.WIDTH // MAX_OPTION_STR_LEN, self.HEIGHT // 4))

        for option in self.game_over_menu.options:
            OPTION_TEXT = OPTION_FONT.render(
                option,
                False,
                YELLOW if option == self.game_over_menu.option else BRIGHT_GREY
            )
            self.window.blit(OPTION_TEXT, TEXT_POS)
            TEXT_POS[1] += OPTION_TEXT.get_height()

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
        outline = pygame.Surface((BOARD_WIDTH + (Window.BORDER_WIDTH << 1), self.BOARD_HEIGHT + (Window.BORDER_WIDTH << 1)))
        outline.fill(BRIGHT_GREY)
        self.window.blit(outline, (BOARD_POS[0] - Window.BORDER_WIDTH, BOARD_POS[1] - Window.BORDER_WIDTH))

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
                                     pygame.Rect(ci * BLOCK_WIDTH + BOARD_POS[0],
                                                 ri * BLOCK_WIDTH + BOARD_POS[1],
                                                 BLOCK_WIDTH,
                                                 BLOCK_WIDTH))

        # draw next piece in its own little box beside the board
        NEXT_PIECE: game.game_2d.Piece = self.controls.game.next_piece

        NEXT_PIECE_BOX_HEIGHT = NEXT_PIECE.piece_height * BLOCK_WIDTH
        NEXT_PIECE_BOX_WIDTH = NEXT_PIECE.piece_height * BLOCK_WIDTH

        outline = pygame.Surface(
            (
                NEXT_PIECE_BOX_WIDTH + (Window.BORDER_WIDTH << 1),
                NEXT_PIECE_BOX_HEIGHT + (Window.BORDER_WIDTH << 1)
            )
        )
        outline.fill(BRIGHT_GREY)

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
        
        BOARD_RIGHT = BOARD_POS[0] + BOARD_WIDTH

        # Next box rendering complete, now it's time to blit the next box.
        # First the outline.
        # Its outline will be overlayed on the board's outline.
        self.window.blit(
            outline,
            (
                BOARD_RIGHT,
                BOARD_POS[1] + (self.BOARD_HEIGHT >> 1) - (outline.get_height() >> 1)
            )
        )
        self.window.blit(
            next_piece_box,
            (
                BOARD_RIGHT + Window.BORDER_WIDTH,
                BOARD_POS[1] + (self.BOARD_HEIGHT >> 1) - (next_piece_box.get_height() >> 1)
            )
        )
    
    def draw_3d(self):
        """
        Draws the 'self.game_control.game' board, piece
        and next piece (TODO), AFTER drawing a grid backgound
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
        """

        if self.mode_menu.option != "3D":
            raise TypeError("Game mode is 2D, but 'draw_3d' was called!")

        slices = [{} for slice_pos in range(game.game_3d.FLOOR_WIDTH)]
        for block_pos_in_game, block_color in self.controls.game.board.items():
            slices[block_pos_in_game[1]][block_pos_in_game] = block_color
        for block_pos_in_game in self.controls.game.piece.block_positions():
            slices[block_pos_in_game[1]][block_pos_in_game] = self.controls.game.piece.color
        # Each FRONT-FACING SLICE of the board, AS IF IT INCLUDED THE PIECE'S BLOCKS,
        # as dictionaries of 3D positions and colors

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
        SLICES_LATTICE_POINTS_IN_SCREEN[y_in_game, x_in_game] -> slice lattice point (row? column?)
        SLICES_LATTICE_POINTS_IN_SCREEN[y_in_game, x_in_game, z_in_game] -> slice lattice point

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
