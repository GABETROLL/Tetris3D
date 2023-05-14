import pygame
from pieces import *

BRIGHT_GREY = (128, 128, 128)
BLACK = (0, 0, 0)

RAINBOW = [(255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255)]


class Controls:
    def __init__(self, window):
        self.window = window

        self.game = Board()

        self.frame_count = 0

        self.das_bar = [15, 6]
        self.das = {LEFT: {"previous_frame": False, "first_das": False, "charge": 0},
                    RIGHT: {"previous_frame": False, "first_das": False, "charge": 0}}
        # "DAS" = "delayed auto shift".

    def main(self, key_down_keys: set[int]):
        self.frame_count += 1
        self.input_handler(key_down_keys)

        if self.frame_count == self.fall_rate(self.game.score_manager.level):
            self.game.play()
            self.frame_count = 0
    # Counting frames.

    @staticmethod
    def fall_rate(level):
        if level <= 8:
            return - 5 * level + 48
        elif level == 9:
            return 6
        elif 10 <= level <= 12:
            return 5
        elif 13 <= level <= 15:
            return 4
        elif 16 <= level <= 18:
            return 3
        elif 19 <= level <= 28:
            return 2
        else:
            return 1
    # Pieces fall faster in higher levels; NES Tetris rules.

    def input_handler(self, key_down_keys: set[int]):
        """Checks w, a, s, d, space bar, period and comma for in-game moves.
        Keeps track of left and right's das."""
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.das[LEFT]["charge"] += 1

            if self.das[LEFT]["charge"] == 6 and self.das[LEFT]["first_das"] or\
                    self.das[LEFT]["charge"] == 15:
                self.game.try_move(LEFT)
                self.das[LEFT]["charge"] = 0
                self.das[LEFT]["first_das"] = True

            elif not self.das[LEFT]["previous_frame"]:
                self.game.try_move(LEFT)
                self.das[LEFT]["charge"] = 0
                self.das[LEFT]["previous_frame"] = True

        else:
            if self.das[LEFT]["charge"] > 0:
                self.das[LEFT]["charge"] -= 1
            self.das[LEFT]["first_das"] = False
            self.das[LEFT]["previous_frame"] = False

        if keys[pygame.K_d]:
            self.das[RIGHT]["charge"] += 1

            if self.das[RIGHT]["charge"] == 6 and self.das[RIGHT]["first_das"] or\
                    self.das[RIGHT]["charge"] == 15:
                self.game.try_move(RIGHT)
                self.das[RIGHT]["charge"] = 0
                self.das[RIGHT]["first_das"] = True

            elif not self.das[RIGHT]["previous_frame"]:
                self.game.try_move(RIGHT)
                self.das[RIGHT]["charge"] = 0
                self.das[RIGHT]["previous_frame"] = True

        else:
            if self.das[RIGHT]["charge"] > 0:
                self.das[RIGHT]["charge"] -= 1
            self.das[RIGHT]["first_das"] = False
            self.das[RIGHT]["previous_frame"] = False

        # If we press left or right, we charge the das bar.
        # The first frame the user presses the direction, the piece moves instantly.
        # The second time is called "first_das", where we wait 15 frames to move the piece.
        # All the other times, we reach up to 6.
        # If user isn't moving, the charge goes down until it reaches 0, and "previous_frame" is set to False.

        if keys[pygame.K_s]:
            self.game.try_move(SOFT_DROP)

        if pygame.K_SPACE in key_down_keys:
            self.game.try_move(HARD_DROP)

            self.frame_count = self.fall_rate(self.game.score_manager.level)
            # If we hard dropped, the dropping cycle of the pieces will reset.

        if pygame.K_PERIOD in key_down_keys:
            self.game.try_rotate()

        if pygame.K_COMMA in key_down_keys:
            self.game.try_rotate(False)


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
    def __init__(self, width: int, height: int, board_width: int, font: pygame.font.Font):
        self.WIDTH = width
        self.HEIGHT = height

        self.BOARD_WIDTH = board_width
        self.BOARD_HEIGHT = board_width * (ROWS // COLUMNS)

        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.running = True

        self.font = font

        self.fps = 60
        self.controls = Controls(self.window)

        self.playing = False

        self.level_menu = Menu(range(20))
        self.mode_menu = Menu(("2D", "3D"))
        self.music_menu = Menu(("Tetris Theme", "Silence"))

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
        self.controls = Controls(self.window)
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

        menu_menu = Menu((self.level_menu, self.mode_menu, self.music_menu))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    menu_menu.move_to_next()
                    print(menu_menu.option)
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    menu_menu.move_to_previous()
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    menu_menu.option.move_to_next()
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    menu_menu.option.move_to_previous()

                if event.key == pygame.K_RETURN:
                    self.init_game()
                    self.playing = True

        self.window.blit(TITLE, (20, 50))

        self.window.blit(STARTING_LEVEL_TEXT, (20, 100))
        CHOSEN_LEVEL_TEXT = CHOSEN_OPTION_FONT.render(str(menu_menu.options[0].option), False, BRIGHT_GREY)
        self.window.blit(CHOSEN_LEVEL_TEXT, (20, 150))

        self.window.blit(GAME_MODE_TEXT, (20, 200))
        CHOSEN_GAME_MODE_TEXT = CHOSEN_OPTION_FONT.render(str(menu_menu.options[1].option), False, BRIGHT_GREY)
        self.window.blit(CHOSEN_GAME_MODE_TEXT, (20, 250))

        self.window.blit(BACKGROUND_MUSIC_TEXT, (20, 300))
        CHOSEN_MUSIC_TEXT = CHOSEN_OPTION_FONT.render(str(menu_menu.options[2].option), False, BRIGHT_GREY)
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

        self.draw_board()
        self.draw_piece()
        self.draw_score()

        self.controls.main(key_down_keys)

    @property
    def board_pos(self):
        """returns (x_pos, y_pos) of the board."""
        return self.WIDTH // 2 - self.BOARD_WIDTH // 2, self.HEIGHT // 2 - self.BOARD_HEIGHT // 2

    @property
    def block_width(self):
        """returns block's width."""
        return self.BOARD_WIDTH // COLUMNS

    def draw_board(self):
        """Draw's board's outline."""
        outline = pygame.Surface((self.BOARD_WIDTH + 40, self.BOARD_HEIGHT + 40))
        outline.fill(BRIGHT_GREY)
        self.window.blit(outline, (self.board_pos[0] - 20, self.board_pos[1] - 20))

        board = pygame.Surface((self.BOARD_WIDTH, self.BOARD_HEIGHT))
        board.fill(BLACK)
        self.window.blit(board, self.board_pos)

        for piece in self.controls.game.board:
            pygame.draw.rect(self.window, self.controls.game.board[piece],
                             pygame.Rect(piece[0] * self.block_width + self.board_pos[0],
                                         piece[1] * self.block_width + self.board_pos[1],
                                         self.block_width,
                                         self.block_width))

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

    def draw_piece(self):
        """Draws piece in the position in the screen in the board."""

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


if __name__ == "__main__":
    pygame.init()
    Window(800, 800, 400, pygame.font.SysFont("consolas", 30))
