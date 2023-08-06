"""
Source: https://tetris.wiki/Super_Rotation_System
"""

SRS_CHECKS = {
    3: [
        [
            [[ 0, 0], 	[1, 0], 	[1,1], 	[ 0,-2], 	[1,-2]],
            [[ 0, 0], 	[-1, 0], 	[-1,1], 	[ 0,-2], 	[-1,-2]]
        ],
        [
            [[ 0, 0], 	[1, 0], 	[1,-1], 	[ 0,2], 	[1,2]],
            [[ 0, 0], 	[1, 0], 	[1,-1], 	[ 0,2], 	[1,2]]
        ],
        [
            [[ 0, 0], 	[-1, 0], 	[-1,1], 	[ 0,-2], 	[-1,-2]],
            [[ 0, 0], 	[1, 0], 	[1,1], 	[ 0,-2], 	[1,-2]]
        ],
        [
            [[ 0, 0], 	[-1, 0], 	[-1,-1], 	[ 0,2], 	[-1,2]],
            [[ 0, 0], 	[-1, 0], 	[-1,-1], 	[ 0,2], 	[-1,2]]
        ]
    ],
    4: [
        [
            [[ 0, 0], 	[-1, 0], 	[2, 0], 	[-1,2], 	[2,-1]],
            [[ 0, 0], 	[-2, 0], 	[1, 0], 	[-2,-1], 	[1,2]]
        ],
        [
            [[ 0, 0], 	[2, 0], 	[-1, 0], 	[2,1], 	[-1,-2]],
            [[ 0, 0], 	[-1, 0], 	[2, 0], 	[-1,2], 	[2,-1]]
        ],
        [
            [[ 0, 0], 	[1, 0], 	[-2, 0], 	[1,-2], 	[-2,1]],
            [[ 0, 0], 	[2, 0], 	[-1, 0], 	[2,1], 	[-1,-2]]
        ],
        [
            [[ 0, 0], 	[-2, 0], 	[1, 0], 	[-2,-1], 	[1,2]],
            [[ 0, 0], 	[1, 0], 	[-2, 0], 	[1,-2], 	[-2,1]]
        ]
    ]
}
"""
A dictionary of matrix sizes [3x3 or 4x4 stored as 3 or 4], and
    a list acting as a dictionary of piece rotation states [0 R 2 or L as indexes 0 1 2 or 3], and
        a list acting as a dictionary of the rotation direction [False or True as indexes 0 or 1],

THE DATA IS UPSIDE DOWN.
"""

for matrix_SRS_checks in SRS_CHECKS.values():
    for initial_rotation_SRS_checks in matrix_SRS_checks:
        for SRS_checks in initial_rotation_SRS_checks:
            for SRS_check in SRS_checks:
                SRS_check[1] *= -1
# FLIPPING DATA VERTICALLY
