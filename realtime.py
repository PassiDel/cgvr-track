import asyncio
import numpy as np

from Wiimote import Wiimote
from calib import calibrate, triangulate
from flask import Flask, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
calib_files = [
    ['weiss_raum', 'weiss_raum_2'],
    ['schwarz', 'schwarz_2'],
    ['weiss_fenster', 'weiss_fenster_2']
]

P1, P2 = calibrate(0, 2)

amount = 2
cache: list[list[tuple[float, float]]] = []
count = 0

messages = []


@app.route("/stream")
def stream():
    def eventStream():
        last = 0
        yield "event: ping\n\n"
        while True:
            # Poll data from the database
            # and see if there's a new message
            if len(messages) > last:
                last += 1
                yield """event: data
data: [{}]

""".format(",".join([str(d) for d in messages[last - 1]]))

    return Response(eventStream(), mimetype="text/event-stream")


def main():
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
    if len(cache[0 if id == 1 else 1]) > 0:
        cord = triangulate(P1, P2, np.array(cache[0][-1]).T, np.array(cache[1][-1]).T)
        print(cord)
        messages.append(cord)
        cache = [[] for _ in range(amount)]
        count = 0

main()
