import numpy as np

from calib import calibrate, triangulate
from flask import Flask, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

P1, P2 = calibrate(0, 2)

messages = []


@app.route("/stream")
def stream():
    def eventStream():
        last = 0
        yield "event: ping\n\n"
        while True:
            if len(messages) > last:
                last += 1
                yield """event: data
data: [{}]

""".format(",".join([str(d) for d in messages[last - 1]]))

    return Response(eventStream(), mimetype="text/event-stream")


data = [
    [[677, 252], [568, 486]],
    [[679, 251], [567, 485]],
    [[729, 308], [518, 465]],
    [[493, 499], [691, 249]],
]

for d in data:
    cord = triangulate(P1, P2, np.array(d[0]).T, np.array(d[1]).T)
    print(cord)
    messages.append(cord)
