import numpy as np

from calib import calibrate, triangulate

P1, P2 = calibrate(0, 2)

data = [
    [[677, 252], [568, 486]],
    [[679, 251], [567, 485]],
    [[729, 308], [518, 465]],
    [[493, 499], [691, 249]],
]

for d in data:
    cord = triangulate(P1, P2, np.array(d[0]).T, np.array(d[1]).T)
    print(cord)
