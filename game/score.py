from dataclasses import dataclass


NO_T_SPIN = 0
MINI_T_SPIN = 1
T_SPIN = 2

T_SPIN_TYPES = (NO_T_SPIN, MINI_T_SPIN, T_SPIN)


@dataclass
class ModernScore:
    points: int = 0
    lines: int = 0
    level: int = 0
    back_to_back: bool = False
    combo_count: int = 0

    def score_soft_drop(self, blocks_traveled: int):
        self.points += blocks_traveled

    def score_hard_drop(self, blocks_traveled: int):
        self.points += (blocks_traveled << 1)

    def score_clear(self, cleared_lines: int, t_spin_type: int, was_all_clear: bool = False) -> None:
        just_line_clear_scores = 0, 100, 300, 500, 800

        points_gained = self.level + 1

        # t-spin / mini t-spin / normal
        if t_spin_type == T_SPIN:
            points_gained *= (400 + 400 * cleared_lines)
        elif t_spin_type == MINI_T_SPIN:
            points_gained *= 100 * (1 << cleared_lines)
        else:
            points_gained *= just_line_clear_scores[cleared_lines]

        # all clear
        if was_all_clear:
            pass

        # back-to-back
        if self.back_to_back:
            points_gained *= 1.5
        if cleared_lines >= 4 or (t_spin_type == MINI_T_SPIN and cleared_lines) or (t_spin_type == T_SPIN and cleared_lines):
            self.back_to_back = True
        else:
            self.back_to_back = False

        # combo
        points_gained += 50 * self.combo_count * self.level
        if cleared_lines:
            self.combo_count += 1
        else:
            self.combo_count = 0


@dataclass
class Score:
    points: int = 0
    lines: int = 0
    level: int = 0
    transitioned: bool = False

    def score(self, cleared_lines: int):
        """
        Updates 'self's fields if the based on the amount of lines cleared,
        in 'cleared_lines'.

        Updates 'points' based on the amount of lines,
        Adds 'cleared_lines' to 'lines',
        and transitions the level like in NES Tetris.
        """
        score_per_line = 0, 40, 100, 300, 1200

        self.points += (self.level + 1) * score_per_line[cleared_lines]
        next_lines = self.lines + cleared_lines

        if self.transitioned and 0 in (n % 10 for n in range(self.lines + 1, next_lines + 1)) and cleared_lines:
            # If we passed or are in a multiple of 10 after transition...
            self.level += 1

        elif self.lines < (self.level + 1) * 10 <= next_lines:
            # If we passed or are in a transition point...
            self.level += 1
            self.transitioned = True
            # NES Tetris rules. :)

        self.lines = next_lines
