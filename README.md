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
```
W          : (3D only) to move to the BACK
A          : (2D & 3D) to move LEFT
S          : to move DOWN (2D) or FRONT (3D)
D          : (2D & 3D) to move RIGHT
LEFT_SHIFT : (2D & 3D) to soft-drop (move piece down gradually)
SPACEBAR   : (2D & 3D) to HARD-DROP (teleport piece to its landing position)
```
### Rotate Piece
In 2D:
```
U: rotate counter-clockwise
O: rotate clockwise
```
In 3D:
```
U : rotate counter-clockwise around the Y axis
O : rotate clockwise around the Y axis
I : rotate counter-clockwise around the X axis
K : rotate clockwise around the X axis
J : rotate clockwise around the Z axis
L : rotate counter-clockwise around the Z axis
```
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
