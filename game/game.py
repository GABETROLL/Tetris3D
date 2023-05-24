from numpy import ndarray
from dataclasses import dataclass


@dataclass
class Piece:
    """
    Tetromino template. Could be 2D or 3D.
    Has a numpy array of ints that will be treated as
    booleans, a position set to [0, 0,...], according to the dimensions of 'piece',
    and a color for the piece.
    """
    def __init__(self, piece: ndarray, color: tuple[int, int, int]):
        if len(piece.shape) not in (2, 3):
            raise ValueError(f"'piece' isn't 2D or 3D!")
        if tuple(len(piece) for _ in piece) != piece.shape:
            raise ValueError(f"'piece' doesn't have all sides the same! Got: {piece}")
        
        self.piece = piece
        self.color = color
        self.pos = [0 for _ in len(piece)]

    def block_positions(self):
        """
        Returns all of the piece's positions
        relative to the board.
        (aka: 'self.pos' + block_pos, as 3D vectors)
        """
        positions = []

        for x_pos, vertical_slice in enumerate(self.piece):
            for y_pos, column in enumerate(vertical_slice):
                for z_pos, block in enumerate(column):
                    if block:
                        positions.append(
                            (x_pos + self.pos[0], y_pos + self.pos[1], z_pos + self.pos[2])
                        )
        return positions

    def relative_block_positions(self):
        """
        Returns all of the block's positions relative
        to the PIECE position, AKA the top-left-front position
        """
        positions = []

        for x_pos, vertical_slice in enumerate(self.blocks):
            for y_pos, column in enumerate(vertical_slice):
                for z_pos, block in enumerate(column):
                    if block:
                        positions.append((x_pos, y_pos, z_pos))
        return positions

