# Tetris3D!
## Requirements
### Python
<img src="https://www.python.org/static/img/python-logo.png" alt="Python logo"/>\
https://www.python.org/\
(This project was developed in version 3.11)\
Install on Debian/Debian-based Linux:
```
$ sudo apt install build-essential checkinstall \
    libreadline-gplv2-dev  libncursesw5-dev libssl-dev \
    libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
$ sudo add-apt-repository ppa:deadsnakes/ppa
$ sudo apt install python3.11
```
Verify Python3.11 is installed:\
Linux:
```
$ python3.11 -m pip --version
```
Windows:
```
$ python -m pip --version
```
### PIP
<img src="https://pypi.org/static/images/logo-small.2a411bc6.svg" alt="PIP logo"/>\
https://pip.pypa.io/en/stable/installation/\
-or-\
https://packaging.python.org/en/latest/tutorials/installing-packages/#ensure-you-can-run-pip-from-the-command-line
### Git
<img src="https://git-scm.com/images/logo@2x.png" alt="Git logo"/>\
https://git-scm.com/downloads\
On Debian-based Linux:
```
$ sudo apt install git
```
### Pygame
<img src="https://www.pygame.org/images/logo_lofi.png" alt="Pygame logo"/>\
https://www.pygame.org/wiki/GettingStarted\

## Installation
```
$ git clone git@github.com:GABETROLL/Tetris3D.git
$ cd Tetris3D/
```
## Run
```
$ python3.11 main.py
```
## Rules
There are 2 ame types: 2D and 3D.
The game starts off with:
- a board
    If the game mode is 2D, the board is 10 x 20.
    If the game mode is 3D, the board is 4 x 4 x 20.
    ![10x20 Tetris board and lines showin its dimensions](https://github.com/GABETROLL/Tetris3D/blob/master/images/3D_dimensions.png?raw=true)\
    ![4x4x20 Tetris board with grid lines in the sides behind it and lines showin its dimensions](https://github.com/GABETROLL/Tetris3D/blob/master/images/2D_dimensions.png?raw=true)

- a random piece, spawned at the top of the board, that the player can control and drop. It falls every N frames, N being faster the higher the level
- a next piece preview.
    It can rotate in 2 directions when the game mode is 2D, and 6 directions when it's 3D.
- a level that determines the speed the pieces fall in

The player can control this piece by:
- moving it in any horizontal direction,
- lower it gradually (SOFT-DROP),
- teleport it to its landing position (HARD-DROP)
- rotating it in the available axii

Every N frames, the piece moves one block down, to fall. If the current level is higher, the piece falls faster.

When a piece lands on top of another block, or the bottom of the board, the piece displayed in the next piece preview spawns as the current piece, and a new 'next piece' gets spawned. This process could go on forever.

When a whole row/floor gets full, that row/floor gets removed from the board, and gets counted to the score. The more rows/floors cleared at the same time, the more points. (The max amount of floors you're able to clear at once is 4)

If a player clears a certain amount of lines, the game "transitions": the level increases, then the levels keep increasing every 10 lines.

The goal is to get as much points as possible, before the pieces stack too high.

When the 'next piece' tries to spawn at the top of the board as the new current piece, but any block in the board blocks it, the game ends.

## Controls
### Move piece
| Key | Direction In 2D | Direction in 3D |
| --- | --------------- | --------------- |
| W   |                 | BACK            |
| A          | LEFT | LEFT |
| S          | DOWN/SOFT-DROP | FRONT |
| D          | RIGHT | RIGHT |
| LEFT_SHIFT | DOWN/SOFT-DROP | DOWN/SOFT-DROP |
| SPACEBAR   | HARD-DROP | HARD-DROP |
![key-direction pair illustration with 2D board screenshot and arrows](https://github.com/GABETROLL/Tetris3D/blob/master/images/2D_moves.png?raw=true)
![key-direction pair illustration with 3D board screenshot and arrows](https://github.com/GABETROLL/Tetris3D/blob/master/images/3D_moves.png?raw=true)
### Rotate Piece
| key | axis | clockwise | 2D | 3D |
| --- | ---- | --------- | -- | -- |
| U   | Y    | False     | :heavy_check_mark: | :heavy_check_mark: |
| O   | Y    | True      | :heavy_check_mark: | :heavy_check_mark: |
| I   | X    | False     |  | :heavy_check_mark: |
| K   | X    | True      |  | :heavy_check_mark: |
| J   | Z    | True      |  | :heavy_check_mark: |
| L   | Z    | False     |  | :heavy_check_mark: |
--------------------------------------------------
The 3D controls are just the 2D controls, with 2 more axii of rotation, relative to the player's "POV".
### Moving in menu screens
Move between (inner) menus:
```
W/UP
S/DOWN
```
Change menu option:
```
A/LEFT  : go to previous option
D/RIGHT : go to next option
```
## Code Documentation
### File Structure & Definitions
```
game/
    score.py
        Score
    move_data.py
        LEFT
        RIGHT
        SOFT_DROP
        HARD_DROP
        BACK
        FRONT
        MOVES_2D
        MOVES_3D
    game_2d.py
        I
        J
        L
        O
        S
        T
        Z
        ROWS: int
        COLUMNS: int
        Piece2D
        Game2D
            pieces = [I, J, L, O, S, T, Z]
            piece: Piece2D
            next_piece: Piece2D
            score_manager: Score
    game_3d.py
        I_3D
        J_3D
        L_3D
        O_3D
        S_3D
        T_3D
        Z_3D
        FLOOR_WIDTH: int
        FLOORS: int
        Piece3D
        Game3D:
            piece: Piece3D
            next_piece: Piece3D
            score_manager: Score
game_control.py
    GameControl
        game: Game2D
        das: dict[str, int]
    GameControl2D(GameControl)
    GameControl3D(GameControl)
main.py
    Menu
    Window
        controls: GameControl
        game_options_menu: Menu

```
### Object Structure
(relative to ``main.py``)
```
Menu
    options: object
    option_index: int
    option -> options[option_index]

Window
    window: pygame.Surface
    BOARD_HEIGHT: int
    HEIGHT: int = BOARD_HEIGHT
    WIDTH: int = HEIGHT

    window: pygame.Surface
    clock = pygame.time.Clock()
    fps: int
    running: bool = True

    font: pygame.font.Font

    level_menu = Menu(range(20))
    mode_menu = Menu(("2D", "3D"))
    music_menu = Menu(("Tetris Theme", "Silence"))
    game_options_menu = Menu((self.level_menu, self.mode_menu, self.music_menu))

    controls: GameControl
        window: pygame.Surface
        game: Game2D | Game3D
            piece: Piece2D | Piece3D
                pos: <2D | 3D pos>
                color: <color>
            next_piece: Piece2D | Piece3D
            board: dict[<2D pos>, <color>] | dict[<3d pos>, <color>]
        das: dict

    frame_handler: bound method
    """
    current "mode" the program is in,
    a method that will be called each frame.
    The methods can be:
    'self.handle_title_screen_frame',
    'self.handle_game_frame',
    'self.handle_game_over_screen_frame'
    """

    game_over_menu =  Menu(("Back to title screen", "Quit"))
        
```
