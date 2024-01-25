import asyncio
import sys
import numpy as np
import cv2

from Wiimote import Wiimote

chessboard_size = (4, 3)

objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), dtype=np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2) * 2

cache: list[list[tuple[float, float]]] = []
output: list[list[tuple[float, float]]] = []

amount = int(sys.argv[1] if len(sys.argv) > 1 else '1')

collect = False


def reset():
    global cache
    cache = [[] for _ in range(amount)]


async def main():
    global collect, cache, output
    reset()
    wiimotes = [Wiimote(i + 1) for i in range(amount)]
    for wiimote in wiimotes:
        wiimote.subscribe(callback)
        output.append([])

    for point in objp:
        print(f"Press enter when {point} is set")
        input()
        collect = True
        print("Collecting data")
        await asyncio.sleep(2)
        collect = False
        print(f"Collected {', '.join([str(len(k)) for k in cache])}")
        for i, e in enumerate(cache):
            output[i].append((
                np.mean([d[0] for d in e]),
                np.mean([d[1] for d in e])
            ))
        print(output)
        with open("output.txt", "w") as text_file:
            text_file.write(str(output))
        reset()
    with open("output.txt", "w") as text_file:
        text_file.write(str(output))
    sys.exit(0)
    # Calibration for each camera
    # ret1, mtx1, dist1, rvecs1, tvecs1 = cv2.calibrateCamera(objp[:10], output[0],(1024, 768), gray.shape[::-1], None, None)
    # ret2, mtx2, dist2, rvecs2, tvecs2 = cv2.calibrateCamera(objp[:10], output[1],(1024, 768), gray.shape[::-1], None, None)
    # ret3, mtx3, dist3, rvecs3, tvecs3 = cv2.calibrateCamera(objp[:10], output[2],(1024, 768), gray.shape[::-1], None, None)


def callback(id: int, data: list[tuple[float, float]]):
    if len(data) < 1:
        return
    if not collect:
        # print(id, data)
        return
    cache[id].append(data[0])


loop = asyncio.get_event_loop()
try:
    asyncio.ensure_future(main())
    loop.run_forever()
finally:
    loop.close()
