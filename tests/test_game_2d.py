from game import game_2d


instance = game_2d.Game2D()

for rotation in range(4):
    for clockwise in range(2):
        print(instance.SRS_rotation_checks(rotation, clockwise), end="")
    print()
