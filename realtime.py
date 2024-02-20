import asyncio
import sys

import cv2
import numpy as np

from Wiimote import Wiimote
from calib import calibrate_camera, stereo_calibrate, homogeneous_to_cartesian

calib_files = [
    ['weiss_raum', 'weiss_raum_2'],
    ['schwarz', 'schwarz_2'],
    ['weiss_fenster', 'weiss_fenster_2']
]

p13_1, p13_2, q13 = (0, 0, 0)

amount = 2
cache: list[list[tuple[float, float]]] = []
count = 0


def calibrate():
    global p13_1, p13_2, q13
    cam1_dist_coeff, cam1_matrix = calibrate_camera(calib_files[0])
    cam3_dist_coeff, cam3_matrix = calibrate_camera(calib_files[2])

    p13_1, p13_2, q13 = stereo_calibrate(0, 2,
                                         cam1_matrix, cam1_dist_coeff,
                                         cam3_matrix, cam3_dist_coeff)


async def main():
    global cache
    wiimotes = [Wiimote(i + 1) for i in range(amount)]
    for wiimote in wiimotes:
        wiimote.subscribe(callback)

    cache = [[] for _ in range(amount)]


def callback(id: int, data: list[tuple[float, float]]):
    global cache, count
    count += 1
    if len(data) < 1:
        return
    cache[id].append(data[0])
    if len(cache[0 if id == 1 else 1]) > 0 and count > 50:
        print(np.array(cache[0][0]).T, np.array(cache[1][0]).T)
        print(homogeneous_to_cartesian(
            cv2.triangulatePoints(p13_1, p13_2, np.array(cache[0][0]).T, np.array(cache[1][0]).T)))
        cache = [[] for _ in range(amount)]
        count = 0


if __name__ == '__main__':
    calibrate()
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(main())
        loop.run_forever()
    finally:
        loop.close()
