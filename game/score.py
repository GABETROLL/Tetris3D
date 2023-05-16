from dataclasses import dataclass


@dataclass
class Score:
    points: int = 0
    lines: int = 0
    level: int = 0
    transitioned: bool = False

    def score(self, cleared_lines: int):
        """Adds points for each line cleared and goes up levels."""
        score_per_line = 0, 40, 100, 300, 1200
        transitions = {level: (level + 1) * 10 for level in range(8 + 1)} | \
                      {level: 100 for level in range(9, 15 + 1)} | \
                      {level: (level + 50) * 10 for level in range(16, 24 + 1)} | \
                      {level: 200 for level in range(25, 28 + 1)}

        self.points += (self.level + 1) * score_per_line[cleared_lines]
        next_lines = self.lines + cleared_lines

        if self.transitioned and 0 in (n % 10 for n in range(self.lines + 1, next_lines + 1)) and cleared_lines:
            # If we passed or are in a multiple of 10 after transition...
            # print(n % 10 for n in range(self.lines, next_lines))
            # print("HI")
            self.level += 1

        elif self.lines < transitions[self.level] <= next_lines:
            # If we passed or are in a transition point...
            self.level += 1
            self.transitioned = True
            # NES Tetris rules. :)

        self.lines = next_lines
