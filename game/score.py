from dataclasses import dataclass


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

        if self.transitioned and 0 in (
            n %
            10 for n in range(
                self.lines +
                1,
                next_lines +
                1)) and cleared_lines:
            # If we passed or are in a multiple of 10 after transition...
            self.level += 1

        elif self.lines < (self.level + 1) * 10 <= next_lines:
            # If we passed or are in a transition point...
            self.level += 1
            self.transitioned = True
            # NES Tetris rules. :)

        self.lines = next_lines
