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
## Use
```
$ python3.11 main.py
```
## Rules
### 2D
### 3D
## Controls
### Cntrolling the current piece
#### Move
```
W/UP       : (3D only) to move to the BACK
A/LEFT     : (2D & 3D) to move LEFT
S/DOWN     : to move DOWN (2D) or FRONT (3D)
D/RIGHT    : (2D & 3D) to move RIGHT
LEFT_SHIFT : (2D & 3D) to soft-drop (move piece down gradually)
SPACEBAR   : (2D & 3D) to HARD-DROP (teleport piece to its landing position)
```
#### Rotate
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
### 
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
