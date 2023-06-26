import game_control
import unittest


class TestGameControl(unittest.TestCase):
    def test_das(self):
        gc2D = game_control.GameControl2D()
        gc3D = game_control.GameControl3D()

        class KeysLeftTest:
            """
            Impersonates 'pygame.key.get_pressed()',
            AS IF the LEFT keys were being pressed.
            """
            def __getitem__(self, key: int):
                return key in game_control.controls_keys["LEFT"]


        for _ in range(100):
            print(gc2D.direction_input_handler(KeysLeftTest()))
        for _ in range(100):
            print(gc3D.direction_input_handler(KeysLeftTest()))
