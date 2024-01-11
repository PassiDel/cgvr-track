#!/usr/bin/python
import sys

# egg_path = '/var/additional/misc/python3-wiimote/cwiid-3.0.0-py3.11-linux-x86_64.egg'
#
# sys.path.append(egg_path)
import cwiid
import matplotlib.pyplot as plt
import asyncio

from Wiimote import Wiimote, Fakemote


async def main():
    amount = int(sys.argv[1] if len(sys.argv) > 1 else '1')
    print(amount)

    # global sp, fig

    wiimotes = [Wiimote(i + 1) for i in range(amount)]

    # wiimotes =[Wiimote(1), Fakemote(2)]

    plt.ion()
    fig = plt.figure()
    # axe = fig.add_subplot(111)
    gs = fig.add_gridspec(amount, hspace=0)
    axs = gs.subplots(sharex=True, sharey=True)

    for ax in axs:
        ax.set_xlim((0, 1024))
        ax.set_ylim((0, 768))

    sps = [ax.plot([], [], 'bo')[0] for ax in axs]

    print(wiimotes)
    print(sps)

    for i, wiimote in enumerate(wiimotes):
        print(wiimote, i)
        wiimote.subscribe(
            lambda j, d: sps[j].set_data([dd[0] for dd in d], [dd[1] for dd in d]) if len(d) > 0 else sps[j].set_data(
                [],
                []))
        # wiimote.subscribe(lambda j, d: print('out', i, j, wiimote.wiiId, d))

    # sp, = axe.plot([], [], 'bo')
    fig.show()

    while True:
        fig.canvas.draw()
        fig.canvas.flush_events()
        # plt.pause(0.001)


# def callback(mesg_list, time):
#     print('time: %f' % time)
#     for mesg in mesg_list:
#         if mesg[0] == cwiid.MESG_IR:
#             valid_src = False
#             print('IR Report: ', end=' ')
#             x = [p['pos'][0] for p in mesg[1] if p and p['pos']]
#             y = [p['pos'][1] for p in mesg[1] if p and p['pos']]
#             for src in mesg[1]:
#                 if src:
#                     valid_src = True
#                     print(src['pos'], end=' ')
#             if valid_src:
#                 sp.set_data(x, y)
#             if not valid_src:
#                 print('no sources detected')
#             else:
#                 print()


loop = asyncio.get_event_loop()
try:
    asyncio.ensure_future(main())
    loop.run_forever()
finally:
    loop.close()
