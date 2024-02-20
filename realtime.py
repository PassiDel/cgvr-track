import asyncio
import numpy as np

from Wiimote import Wiimote
from calib import calibrate, triangulate

calib_files = [
    ['weiss_raum', 'weiss_raum_2'],
    ['schwarz', 'schwarz_2'],
    ['weiss_fenster', 'weiss_fenster_2']
]

P1, P2 = calibrate(0, 2)

amount = 2
cache: list[list[tuple[float, float]]] = []
count = 0

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
        cord = triangulate(P1, P2, np.array(cache[0][-1]).T, np.array(cache[1][-1]).T)
        print(cord)
        cache = [[] for _ in range(amount)]
        count = 0


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(main())
        loop.run_forever()
    finally:
        loop.close()
