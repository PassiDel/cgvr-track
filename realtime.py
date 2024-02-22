import asyncio
import numpy as np

from Wiimote import Wiimote
from calib import calibrate, triangulate
from flask import Flask, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

P23_1, P23_2 = calibrate(1, 2)
P21_1, P21_2 = calibrate(1, 0)

amount = 3
cache: list[list[tuple[float, float]]] = []

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
    global cache
    if len(data) < 1:
        return
    cache[id].append(data[0])

    cord21 = None
    cord23 = None
    if len(cache[0]) > 0 and len(cache[1]) > 0:
        cord21 = triangulate(P21_1, P21_2, np.array(cache[1][-1]).T, np.array(cache[0][-1]).T) - np.array([0, 0, 46])
        cache[0] = []
    if len(cache[2]) > 0 and len(cache[1]) > 0:
        cord23 = triangulate(P23_1, P23_2, np.array(cache[1][-1]).T, np.array(cache[2][-1]).T) - np.array([0, 0, 46])
        cache[2] = []

    if cord23 is not None and cord21 is not None:
        cord = (cord21 + cord23) / 2
        messages.append(cord)
        cache[1] = []
        print(cord)
    elif cord23 is not None:
        cord = cord23
        messages.append(cord)
        cache[1] = []
        print(cord)
    elif cord21 is not None:
        cord = cord21
        messages.append(cord)
        cache[1] = []
        print(cord)
        messages.append(cord)


main()
